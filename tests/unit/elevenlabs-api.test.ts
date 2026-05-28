import { beforeEach, describe, expect, it, vi } from 'vitest'

// Capture the args passed to SDK methods so we can assert request shape.
const ttsConvertCalls: any[] = []
const dialogueConvertCalls: any[] = []
const modelsListMock = vi.fn()
const voicesSearchMock = vi.fn()
const voicesGetMock = vi.fn()

// Build a tiny fake of the SDK that mirrors the real surface area
// (.textToSpeech.convert(...).withRawResponse()).
vi.mock('@elevenlabs/elevenlabs-js', () => {
  class ElevenLabsClient {
    apiKey: string
    constructor(opts: { apiKey: string }) {
      this.apiKey = opts.apiKey
    }
    get textToSpeech() {
      return {
        convert: (voiceId: string, body: any) => {
          ttsConvertCalls.push({ voiceId, body })
          return {
            withRawResponse: async () => ({
              data: makeStreamFromString('AUDIO'),
              rawResponse: { headers: new Headers({ 'request-id': 'req-123' }) },
            }),
          }
        },
      }
    }
    get textToDialogue() {
      return {
        convert: (body: any) => {
          dialogueConvertCalls.push({ body })
          return {
            withRawResponse: async () => ({
              data: makeStreamFromString('DIALOGUE'),
              rawResponse: { headers: new Headers({ 'request-id': 'req-456' }) },
            }),
          }
        },
      }
    }
    get models() {
      return { list: modelsListMock }
    }
    get voices() {
      return { search: voicesSearchMock, get: voicesGetMock }
    }
  }
  return { ElevenLabsClient }
})

function makeStreamFromString(s: string): ReadableStream<Uint8Array> {
  const bytes = new TextEncoder().encode(s)
  return new ReadableStream({
    start(controller) {
      controller.enqueue(bytes)
      controller.close()
    },
  })
}

beforeEach(() => {
  ttsConvertCalls.length = 0
  dialogueConvertCalls.length = 0
  modelsListMock.mockReset()
  voicesSearchMock.mockReset()
  voicesGetMock.mockReset()
})

describe('generateAudio', () => {
  it('passes a fully-formed TTS request and returns audio + requestId', async () => {
    const { generateAudio } = await import('@/lib/elevenlabs/api')
    const result = await generateAudio({
      apiKey: 'sk-test',
      voiceId: 'voice-1',
      modelId: 'eleven_v3',
      text: '[whispers] hi',
      voiceSettings: {
        stability: 0.4,
        similarity_boost: 0.8,
        style: 0.1,
        use_speaker_boost: true,
        speed: 1.1,
      },
      outputFormat: 'mp3_44100_128',
      seed: 42,
      applyTextNormalization: 'auto',
      previousText: 'prior line',
      previousRequestIds: ['a', 'b', 'c', 'd'],
    })

    expect(ttsConvertCalls).toHaveLength(1)
    const { voiceId, body } = ttsConvertCalls[0]
    expect(voiceId).toBe('voice-1')
    expect(body.modelId).toBe('eleven_v3')
    expect(body.outputFormat).toBe('mp3_44100_128')
    expect(body.seed).toBe(42)
    expect(body.applyTextNormalization).toBe('auto')
    expect(body.previousText).toBe('prior line')
    // Caps previousRequestIds at the last 3.
    expect(body.previousRequestIds).toEqual(['b', 'c', 'd'])
    // Snake-case input is mapped to SDK camel-case fields.
    expect(body.voiceSettings).toEqual({
      stability: 0.4,
      similarityBoost: 0.8,
      style: 0.1,
      useSpeakerBoost: true,
      speed: 1.1,
    })

    expect(new TextDecoder().decode(new Uint8Array(result.audio))).toBe('AUDIO')
    expect(result.requestId).toBe('req-123')
    expect(result.outputFormat).toBe('mp3_44100_128')
  })

  it('omits optional fields when not provided', async () => {
    const { generateAudio } = await import('@/lib/elevenlabs/api')
    await generateAudio({
      apiKey: 'sk-test',
      voiceId: 'voice-1',
      modelId: 'eleven_flash_v2_5',
      text: 'plain',
      voiceSettings: {
        stability: 0.5,
        similarity_boost: 0.5,
        style: 0,
        use_speaker_boost: false,
      },
    })
    const { body } = ttsConvertCalls[0]
    expect(body.seed).toBeUndefined()
    expect(body.applyTextNormalization).toBeUndefined()
    expect(body.previousText).toBeUndefined()
    expect(body.previousRequestIds).toBeUndefined()
    expect(body.voiceSettings.speed).toBeUndefined()
    // Defaults output format to mp3_44100_128.
    expect(body.outputFormat).toBe('mp3_44100_128')
  })
})

describe('generateDialogue', () => {
  it('forwards inputs[] verbatim and wraps stability under settings', async () => {
    const { generateDialogue } = await import('@/lib/elevenlabs/api')
    const result = await generateDialogue({
      apiKey: 'sk-test',
      modelId: 'eleven_v3',
      inputs: [
        { voiceId: 'v1', text: '[whispers] hi' },
        { voiceId: 'v2', text: '[curious] who?' },
      ],
      stability: 0.5,
      seed: 7,
      outputFormat: 'mp3_44100_192',
    })

    expect(dialogueConvertCalls).toHaveLength(1)
    const { body } = dialogueConvertCalls[0]
    expect(body.modelId).toBe('eleven_v3')
    expect(body.outputFormat).toBe('mp3_44100_192')
    expect(body.seed).toBe(7)
    expect(body.settings).toEqual({ stability: 0.5 })
    expect(body.inputs).toEqual([
      { voiceId: 'v1', text: '[whispers] hi' },
      { voiceId: 'v2', text: '[curious] who?' },
    ])
    expect(result.requestId).toBe('req-456')
  })
})

describe('fetchModels / fetchVoices', () => {
  it('filters out non-TTS models and maps to snake_case', async () => {
    modelsListMock.mockResolvedValueOnce([
      { modelId: 'eleven_v3', name: 'Eleven v3', canDoTextToSpeech: true },
      { modelId: 'sts_only', name: 'STS only', canDoTextToSpeech: false },
      { modelId: 'no_flag', name: 'Implicit TTS' }, // canDoTextToSpeech undefined
    ])
    const { fetchModels } = await import('@/lib/elevenlabs/api')
    const models = await fetchModels('sk-test')
    expect(models).toEqual([
      { model_id: 'eleven_v3', name: 'Eleven v3' },
      { model_id: 'no_flag', name: 'Implicit TTS' },
    ])
  })

  it('maps voices.search result to snake_case', async () => {
    voicesSearchMock.mockResolvedValueOnce({
      voices: [{ voiceId: 'v1', name: 'Adam' }, { voiceId: 'v2' }],
    })
    const { fetchVoices } = await import('@/lib/elevenlabs/api')
    const voices = await fetchVoices('sk-test')
    expect(voices).toEqual([
      { voice_id: 'v1', name: 'Adam' },
      { voice_id: 'v2', name: 'Unnamed voice' },
    ])
  })
})

describe('extensionForOutputFormat', () => {
  it('maps formats to file extensions', async () => {
    const { extensionForOutputFormat } = await import('@/lib/elevenlabs/api')
    expect(extensionForOutputFormat('mp3_44100_128')).toBe('mp3')
    expect(extensionForOutputFormat('pcm_24000')).toBe('pcm')
    expect(extensionForOutputFormat('ulaw_8000')).toBe('ulaw')
  })
})
