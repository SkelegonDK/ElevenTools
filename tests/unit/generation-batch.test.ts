import { beforeEach, describe, expect, it } from 'vitest'
import {
  deriveName,
  runBatch,
  runDialogue,
  type GenerateCall,
  type GenerationPorts,
  type PersistedRow,
} from '@/lib/generation/batch'
import { parseBatchRequest, parseDialogueRequest } from '@/lib/generation/request'

/**
 * The in-memory adapter at the generation seam. No HTTP, no filesystem, no
 * database — the whole batch run is exercised through `runBatch`'s interface.
 */
function inMemoryPorts(
  options: {
    failOn?: number[]
    requestIds?: (index: number) => string | null
  } = {}
) {
  const generateCalls: GenerateCall[] = []
  const dialogueCalls: unknown[] = []
  const saved: Array<{ batchId: string; name: string; ext: string; size: number }> = []
  const persisted: PersistedRow[] = []
  let call = 0
  let ids = 0

  const ports: GenerationPorts = {
    async generateAudio(c) {
      const index = call++
      generateCalls.push(c)
      if (options.failOn?.includes(index)) {
        throw new Error(`row ${index} exploded`)
      }
      const requestId = options.requestIds ? options.requestIds(index) : `req-${index}`
      return { audio: new TextEncoder().encode(`AUDIO-${index}`).buffer, requestId }
    },
    async generateDialogue(c) {
      dialogueCalls.push(c)
      return { audio: new TextEncoder().encode('DIALOGUE').buffer, requestId: 'req-d' }
    },
    newBatchId: (prefix) => `${prefix}-fixed`,
    newGenerationId: () => `gen-${ids++}`,
    save(batchId, name, ext, bytes) {
      saved.push({ batchId, name, ext, size: bytes.byteLength })
      const filename = `${name}.${ext}`
      return { filename, url: `/api/audio/${batchId}/${filename}` }
    },
    persist: (row) => void persisted.push(row),
  }

  return { ports, generateCalls, dialogueCalls, saved, persisted }
}

function request(rows: Array<Record<string, string>>, overrides: Record<string, unknown> = {}) {
  const parsed = parseBatchRequest({
    rows,
    voiceId: 'voice-1',
    modelId: 'eleven_v3',
    ...overrides,
  })
  if (!parsed.ok) throw new Error(parsed.error)
  return parsed.value
}

describe('deriveName', () => {
  it('falls back to a positional name', () => {
    expect(deriveName({ text: 'hi' }, 0)).toBe('audio_1')
    expect(deriveName({ text: 'hi' }, 4)).toBe('audio_5')
  })

  it('substitutes row variables into the template', () => {
    expect(deriveName({ text: 'hi', filename: 'greet_{name}', name: 'ada' }, 0)).toBe('greet_ada')
  })

  it('ignores a blank template', () => {
    expect(deriveName({ text: 'hi', filename: '   ' }, 0)).toBe('audio_1')
  })

  it('leaves an unknown variable in place', () => {
    expect(deriveName({ text: 'hi', filename: 'x_{missing}' }, 0)).toBe('x_{missing}')
  })
})

describe('runBatch — prosody continuity', () => {
  let ctx: ReturnType<typeof inMemoryPorts>

  beforeEach(() => {
    ctx = inMemoryPorts()
  })

  it('gives each row its neighbours as previousText / nextText', async () => {
    await runBatch(request([{ text: 'one' }, { text: 'two' }, { text: 'three' }]), ctx.ports)

    const [first, second, third] = ctx.generateCalls
    expect(first.previousText).toBeUndefined()
    expect(first.nextText).toBe('two')

    expect(second.previousText).toBe('one')
    expect(second.nextText).toBe('three')

    expect(third.previousText).toBe('two')
    expect(third.nextText).toBeUndefined()
  })

  it('uses substituted text for the neighbour hints, not the raw template', async () => {
    await runBatch(
      request([
        { text: 'Hi {name}', name: 'Ada' },
        { text: 'Bye {name}', name: 'Bob' },
      ]),
      ctx.ports
    )
    expect(ctx.generateCalls[0].nextText).toBe('Bye Bob')
    expect(ctx.generateCalls[1].previousText).toBe('Hi Ada')
  })

  it('sends no request ids on the first row', async () => {
    await runBatch(request([{ text: 'one' }]), ctx.ports)
    expect(ctx.generateCalls[0].previousRequestIds).toBeUndefined()
  })

  it('feeds back a rolling window of the last three request ids', async () => {
    await runBatch(
      request([
        { text: '1' },
        { text: '2' },
        { text: '3' },
        { text: '4' },
        { text: '5' },
      ]),
      ctx.ports
    )
    expect(ctx.generateCalls[1].previousRequestIds).toEqual(['req-0'])
    expect(ctx.generateCalls[3].previousRequestIds).toEqual(['req-0', 'req-1', 'req-2'])
    // Window stays at three — the oldest id drops off.
    expect(ctx.generateCalls[4].previousRequestIds).toEqual(['req-1', 'req-2', 'req-3'])
  })

  it('does not advance the window for a row that failed', async () => {
    const failing = inMemoryPorts({ failOn: [1] })
    await runBatch(request([{ text: '1' }, { text: '2' }, { text: '3' }]), failing.ports)

    // Row 2 never produced a request id, so row 3 still only carries row 1's.
    expect(failing.generateCalls[2].previousRequestIds).toEqual(['req-0'])
  })

  it('skips the window entirely when the provider returns no request id', async () => {
    const ctx3 = inMemoryPorts({ requestIds: () => null })
    await runBatch(request([{ text: '1' }, { text: '2' }]), ctx3.ports)
    expect(ctx3.generateCalls[1].previousRequestIds).toBeUndefined()
  })
})

describe('runBatch — results and errors', () => {
  it('reports success and failure counts side by side', async () => {
    const ctx = inMemoryPorts({ failOn: [1] })
    const result = await runBatch(
      request([{ text: 'a' }, { text: 'b' }, { text: 'c' }]),
      ctx.ports
    )

    expect(result.success).toBe(2)
    expect(result.failed).toBe(1)
    expect(result.results.map((r) => r.index)).toEqual([0, 2])
    expect(result.errors).toEqual([{ index: 1, error: 'row 1 exploded' }])
  })

  it('keeps going after a failure instead of aborting the batch', async () => {
    const ctx = inMemoryPorts({ failOn: [0] })
    const result = await runBatch(request([{ text: 'a' }, { text: 'b' }]), ctx.ports)
    expect(result.results).toHaveLength(1)
    expect(ctx.persisted).toHaveLength(1)
  })

  it('does not persist or save a row that failed to generate', async () => {
    const ctx = inMemoryPorts({ failOn: [0] })
    await runBatch(request([{ text: 'a' }]), ctx.ports)
    expect(ctx.saved).toHaveLength(0)
    expect(ctx.persisted).toHaveLength(0)
  })

  it('returns the batch id it minted', async () => {
    const ctx = inMemoryPorts()
    const result = await runBatch(request([{ text: 'a' }]), ctx.ports)
    expect(result.batchId).toBe('batch-fixed')
    expect(ctx.saved[0].batchId).toBe('batch-fixed')
  })

  it('reports the filename the store actually used, not the requested one', async () => {
    const ctx = inMemoryPorts()
    // The fake store appends the extension; a real one may also dedupe.
    const result = await runBatch(request([{ text: 'a', filename: 'line' }]), ctx.ports)
    expect(result.results[0].filename).toBe('line.mp3')
    expect(result.results[0].url).toBe('/api/audio/batch-fixed/line.mp3')
  })
})

describe('runBatch — persistence', () => {
  it('records one row per generation with the resolved parameters', async () => {
    const ctx = inMemoryPorts()
    await runBatch(
      request([{ text: 'Hi {name}', name: 'Ada' }], {
        seed: 42,
        outputFormat: 'pcm_24000',
      }),
      ctx.ports
    )

    expect(ctx.persisted).toEqual([
      {
        id: 'gen-0',
        batch_id: 'batch-fixed',
        text: 'Hi Ada',
        voice_id: 'voice-1',
        model_id: 'eleven_v3',
        audio_path: '/api/audio/batch-fixed/audio_1.pcm',
        filename: 'audio_1.pcm',
        request_id: 'req-0',
        seed: 42,
        output_format: 'pcm_24000',
        kind: 'tts',
      },
    ])
  })

  it('stores a null seed when none was requested', async () => {
    const ctx = inMemoryPorts()
    await runBatch(request([{ text: 'a' }]), ctx.ports)
    expect(ctx.persisted[0].seed).toBeNull()
  })

  it('passes the format-derived extension to the store', async () => {
    const ctx = inMemoryPorts()
    await runBatch(request([{ text: 'a' }], { outputFormat: 'ulaw_8000' }), ctx.ports)
    expect(ctx.saved[0].ext).toBe('ulaw')
  })
})

describe('runDialogue', () => {
  function dialogueRequest(overrides: Record<string, unknown> = {}) {
    const parsed = parseDialogueRequest({
      modelId: 'eleven_v3',
      inputs: [
        { voiceId: 'v1', text: 'hi' },
        { voiceId: 'v2', text: 'hello' },
      ],
      ...overrides,
    })
    if (!parsed.ok) throw new Error(parsed.error)
    return parsed.value
  }

  it('mints a dialogue-prefixed batch and returns the stored location', async () => {
    const ctx = inMemoryPorts()
    const result = await runDialogue(dialogueRequest(), ctx.ports)

    expect(result.batchId).toBe('dialogue-fixed')
    expect(result.filename).toBe('dialogue.mp3')
    expect(result.url).toBe('/api/audio/dialogue-fixed/dialogue.mp3')
    expect(result.requestId).toBe('req-d')
  })

  it('uses the caller-supplied filename when there is one', async () => {
    const ctx = inMemoryPorts()
    const result = await runDialogue(dialogueRequest({ filename: 'scene-1' }), ctx.ports)
    expect(result.filename).toBe('scene-1.mp3')
  })

  it('persists the transcript with every speaker labelled', async () => {
    const ctx = inMemoryPorts()
    await runDialogue(dialogueRequest(), ctx.ports)
    expect(ctx.persisted[0].text).toBe('[v1] hi\n[v2] hello')
    expect(ctx.persisted[0].kind).toBe('dialogue')
    expect(ctx.persisted[0].voice_id).toBe('v1')
  })
})
