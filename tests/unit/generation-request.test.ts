import { describe, expect, it } from 'vitest'
import {
  DEFAULT_VOICE_SETTINGS,
  DIALOGUE_LIMITS,
  SEED_MAX,
  parseBatchRequest,
  parseDialogueRequest,
  parseSeed,
  resolveVoiceSettings,
} from '@/lib/generation/request'

const V3 = 'eleven_v3'
const V1 = 'eleven_monolingual_v1'

function batchBody(overrides: Record<string, unknown> = {}) {
  return {
    rows: [{ text: 'hello' }],
    voiceId: 'voice-1',
    modelId: V3,
    ...overrides,
  }
}

function dialogueBody(overrides: Record<string, unknown> = {}) {
  return {
    modelId: V3,
    inputs: [{ voiceId: 'v1', text: 'hi' }],
    ...overrides,
  }
}

function expectOk<T>(result: { ok: true; value: T } | { ok: false; error: string }): T {
  if (!result.ok) throw new Error(`expected ok, got: ${result.error}`)
  return result.value
}

function expectError(result: { ok: boolean; error?: string }): string {
  if (result.ok) throw new Error('expected a parse failure')
  return result.error!
}

describe('parseSeed', () => {
  it('treats empty input as no seed', () => {
    expect(expectOk(parseSeed(''))).toBeUndefined()
    expect(expectOk(parseSeed('   '))).toBeUndefined()
  })

  it('accepts the range boundaries', () => {
    expect(expectOk(parseSeed('0'))).toBe(0)
    expect(expectOk(parseSeed(String(SEED_MAX)))).toBe(SEED_MAX)
  })

  it('rejects out-of-range, fractional and non-numeric input', () => {
    expect(expectError(parseSeed('-1'))).toMatch(/between 0 and/)
    expect(expectError(parseSeed(String(SEED_MAX + 1)))).toMatch(/between 0 and/)
    expect(expectError(parseSeed('1.5'))).toMatch(/whole number/)
    expect(expectError(parseSeed('abc'))).toMatch(/whole number/)
  })
})

describe('resolveVoiceSettings', () => {
  it('fills every default when given nothing', () => {
    expect(resolveVoiceSettings(V3, undefined)).toEqual(DEFAULT_VOICE_SETTINGS)
  })

  it('clamps values into range instead of trusting them', () => {
    const settings = resolveVoiceSettings(V3, {
      stability: 99,
      similarity_boost: -4,
      style: 12,
      use_speaker_boost: true,
      speed: 100,
    })
    expect(settings.stability).toBe(1)
    expect(settings.similarity_boost).toBe(0)
    expect(settings.style).toBe(1)
    expect(settings.speed).toBe(4)
  })

  it('ignores non-numeric values and falls back to the default', () => {
    const settings = resolveVoiceSettings(V3, { stability: 'banana' as unknown as number })
    expect(settings.stability).toBe(DEFAULT_VOICE_SETTINGS.stability)
  })

  it('drops style and speaker boost for a model that has neither', () => {
    const settings = resolveVoiceSettings(V1, {
      stability: 0.4,
      style: 0.9,
      use_speaker_boost: true,
    })
    expect(settings.style).toBe(0)
    expect(settings.use_speaker_boost).toBe(false)
    // Stability is model-independent and survives.
    expect(settings.stability).toBe(0.4)
  })

  it('omits speed entirely for a model without speed control', () => {
    expect(resolveVoiceSettings(V1, { speed: 1.5 })).not.toHaveProperty('speed')
  })

  it('omits speed when the caller did not ask for it', () => {
    expect(resolveVoiceSettings(V3, { stability: 0.5 })).not.toHaveProperty('speed')
  })

  it('coerces a non-boolean speaker boost to false', () => {
    const settings = resolveVoiceSettings(V3, {
      use_speaker_boost: 'yes' as unknown as boolean,
    })
    expect(settings.use_speaker_boost).toBe(false)
  })
})

describe('parseBatchRequest', () => {
  it('accepts a minimal body and fills defaults', () => {
    const request = expectOk(parseBatchRequest(batchBody()))
    expect(request.outputFormat).toBe('mp3_44100_128')
    expect(request.voiceSettings).toEqual(DEFAULT_VOICE_SETTINGS)
    expect(request.seed).toBeUndefined()
    expect(request.applyTextNormalization).toBeUndefined()
  })

  it('rejects a non-object body', () => {
    expect(expectError(parseBatchRequest('nope'))).toMatch(/must be an object/)
    expect(expectError(parseBatchRequest(null))).toMatch(/must be an object/)
    expect(expectError(parseBatchRequest([]))).toMatch(/must be an object/)
  })

  it('rejects an empty or missing row list', () => {
    expect(expectError(parseBatchRequest(batchBody({ rows: [] })))).toBe('No rows provided')
    expect(expectError(parseBatchRequest(batchBody({ rows: undefined })))).toBe('No rows provided')
  })

  it('names the row that is missing text', () => {
    const body = batchBody({ rows: [{ text: 'ok' }, { text: '  ' }] })
    expect(expectError(parseBatchRequest(body))).toBe('Row 2 is missing text')
  })

  it('requires voiceId and modelId', () => {
    expect(expectError(parseBatchRequest(batchBody({ voiceId: '' })))).toMatch(/voiceId/)
    expect(expectError(parseBatchRequest(batchBody({ modelId: undefined })))).toMatch(/modelId/)
  })

  it('rejects an output format outside the supported union', () => {
    const error = expectError(parseBatchRequest(batchBody({ outputFormat: 'flac_96000' })))
    expect(error).toMatch(/Unsupported outputFormat/)
  })

  it('rejects an unsupported normalization value', () => {
    const error = expectError(parseBatchRequest(batchBody({ applyTextNormalization: 'maybe' })))
    expect(error).toMatch(/auto, on, off/)
  })

  it('rejects an out-of-range seed rather than passing it to the SDK', () => {
    expect(expectError(parseBatchRequest(batchBody({ seed: -1 })))).toMatch(/seed/)
    expect(expectError(parseBatchRequest(batchBody({ seed: 1.5 })))).toMatch(/seed/)
  })

  it('gates voice settings on the model, not on the caller', () => {
    const body = batchBody({
      modelId: V1,
      voiceSettings: { stability: 0.5, style: 0.9, use_speaker_boost: true, speed: 2 },
    })
    const request = expectOk(parseBatchRequest(body))
    expect(request.voiceSettings.style).toBe(0)
    expect(request.voiceSettings.use_speaker_boost).toBe(false)
    expect(request.voiceSettings).not.toHaveProperty('speed')
  })

  it('trims the identifiers', () => {
    const request = expectOk(parseBatchRequest(batchBody({ voiceId: '  voice-1  ' })))
    expect(request.voiceId).toBe('voice-1')
  })

  it('keeps arbitrary row columns for variable substitution', () => {
    const body = batchBody({ rows: [{ text: 'Hi {name}', name: 'Ada', filename: 'hi_{name}' }] })
    const request = expectOk(parseBatchRequest(body))
    expect(request.rows[0]).toMatchObject({ name: 'Ada', filename: 'hi_{name}' })
  })
})

describe('parseDialogueRequest', () => {
  it('accepts a minimal body and defaults stability', () => {
    const request = expectOk(parseDialogueRequest(dialogueBody()))
    expect(request.stability).toBe(DEFAULT_VOICE_SETTINGS.stability)
    expect(request.outputFormat).toBe('mp3_44100_128')
  })

  it('rejects a model that cannot do dialogue', () => {
    const error = expectError(parseDialogueRequest(dialogueBody({ modelId: 'eleven_flash_v2_5' })))
    expect(error).toMatch(/does not support Text-to-Dialogue/)
  })

  it('enforces the line cap that previously only existed in the UI', () => {
    const inputs = Array.from({ length: DIALOGUE_LIMITS.maxLines + 1 }, () => ({
      voiceId: 'v1',
      text: 'x',
    }))
    expect(expectError(parseDialogueRequest(dialogueBody({ inputs })))).toMatch(
      /Maximum 20 dialogue lines/
    )
  })

  it('enforces the unique-voice cap', () => {
    const inputs = Array.from({ length: DIALOGUE_LIMITS.maxUniqueVoices + 1 }, (_, i) => ({
      voiceId: `v${i}`,
      text: 'x',
    }))
    expect(expectError(parseDialogueRequest(dialogueBody({ inputs })))).toMatch(
      /Maximum 10 unique voices/
    )
  })

  it('enforces the total character budget', () => {
    const inputs = [{ voiceId: 'v1', text: 'x'.repeat(DIALOGUE_LIMITS.maxTotalChars + 1) }]
    expect(expectError(parseDialogueRequest(dialogueBody({ inputs })))).toMatch(
      /Total characters must be/
    )
  })

  it('rejects a line with no voice or no text', () => {
    expect(expectError(parseDialogueRequest(dialogueBody({ inputs: [{ text: 'hi' }] })))).toMatch(
      /voiceId and non-empty text/
    )
    expect(
      expectError(parseDialogueRequest(dialogueBody({ inputs: [{ voiceId: 'v1', text: ' ' }] })))
    ).toMatch(/voiceId and non-empty text/)
  })

  it('clamps stability into range', () => {
    expect(expectOk(parseDialogueRequest(dialogueBody({ stability: 9 }))).stability).toBe(1)
  })

  it('carries the optional filename and languageCode through', () => {
    const request = expectOk(
      parseDialogueRequest(dialogueBody({ filename: ' scene-1 ', languageCode: 'en' }))
    )
    expect(request.filename).toBe('scene-1')
    expect(request.languageCode).toBe('en')
  })
})
