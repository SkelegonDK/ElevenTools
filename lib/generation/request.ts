/**
 * The one owner of "what a generation is".
 *
 * Defaults, ranges, applicability rules, and the wire shape all live here so
 * the pages, the route handlers, and the tests agree by construction rather
 * than by four hand-maintained copies.
 *
 * Deliberately free of `server-only` and of the SDK — client components import
 * the defaults and the option tables from this module.
 */

import {
  DEFAULT_OUTPUT_FORMAT,
  type DialogueInput,
  type OutputFormat,
  type TextNormalization,
  type VoiceSettings,
} from '@/lib/elevenlabs/types'
import { getModelCapabilities } from '@/lib/utils/model-capabilities'

// ── Defaults, ranges, option tables ─────────────────────────────────────────

export const DEFAULT_VOICE_SETTINGS: VoiceSettings = {
  stability: 0.5,
  similarity_boost: 0.5,
  style: 0.0,
  use_speaker_boost: false,
}

export const DEFAULT_STABILITY = DEFAULT_VOICE_SETTINGS.stability

export const VOICE_SETTING_RANGES = {
  stability: { min: 0, max: 1, step: 0.05 },
  similarity_boost: { min: 0, max: 1, step: 0.05 },
  style: { min: 0, max: 1, step: 0.05 },
  speed: { min: 0.25, max: 4, step: 0.05 },
} as const

/** ElevenLabs accepts a uint32 seed. */
export const SEED_MAX = 4294967295

export const NORMALIZATION_OPTIONS: readonly TextNormalization[] = ['auto', 'on', 'off']

const VALID_NORMALIZATION = new Set<string>(NORMALIZATION_OPTIONS)

export const OUTPUT_FORMAT_OPTIONS: ReadonlyArray<{
  value: OutputFormat
  label: string
  hint?: string
}> = [
  { value: 'mp3_44100_128', label: 'MP3 · 44.1kHz · 128 kbps', hint: 'default' },
  { value: 'mp3_44100_192', label: 'MP3 · 44.1kHz · 192 kbps', hint: 'creator+' },
  { value: 'mp3_44100_96', label: 'MP3 · 44.1kHz · 96 kbps' },
  { value: 'mp3_44100_64', label: 'MP3 · 44.1kHz · 64 kbps' },
  { value: 'mp3_44100_32', label: 'MP3 · 44.1kHz · 32 kbps' },
  { value: 'mp3_22050_32', label: 'MP3 · 22.05kHz · 32 kbps' },
  { value: 'pcm_16000', label: 'PCM · 16kHz' },
  { value: 'pcm_22050', label: 'PCM · 22.05kHz' },
  { value: 'pcm_24000', label: 'PCM · 24kHz' },
  { value: 'pcm_44100', label: 'PCM · 44.1kHz', hint: 'pro+' },
  { value: 'pcm_48000', label: 'PCM · 48kHz', hint: 'pro+' },
  { value: 'ulaw_8000', label: 'µ-law · 8kHz', hint: 'telephony' },
]

const VALID_OUTPUT_FORMATS = new Set<string>(OUTPUT_FORMAT_OPTIONS.map((o) => o.value))

export const DIALOGUE_LIMITS = {
  maxUniqueVoices: 10,
  maxTotalChars: 2000,
  maxLines: 20,
} as const

// ── Result type ─────────────────────────────────────────────────────────────

export type ParseResult<T> = { ok: true; value: T } | { ok: false; error: string }

const fail = <T,>(error: string): ParseResult<T> => ({ ok: false, error })
const pass = <T,>(value: T): ParseResult<T> => ({ ok: true, value })

// ── Requests ────────────────────────────────────────────────────────────────

export interface BatchRow {
  text: string
  filename?: string
  [key: string]: string | undefined
}

export interface BatchRequest {
  rows: BatchRow[]
  voiceId: string
  modelId: string
  voiceSettings: VoiceSettings
  outputFormat: OutputFormat
  seed?: number
  applyTextNormalization?: TextNormalization
}

export interface DialogueRequest {
  modelId: string
  inputs: DialogueInput[]
  stability: number
  outputFormat: OutputFormat
  filename?: string
  seed?: number
  applyTextNormalization?: TextNormalization
  languageCode?: string
}

// ── Field-level helpers ─────────────────────────────────────────────────────

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

/**
 * Parse the seed as typed into a text input. Empty means "no seed"; anything
 * that isn't a whole number inside the uint32 range is rejected.
 */
export function parseSeed(raw: string): ParseResult<number | undefined> {
  const trimmed = raw.trim()
  if (trimmed === '') return pass(undefined)
  const n = Number(trimmed)
  if (!Number.isInteger(n) || n < 0 || n > SEED_MAX) {
    return fail(`Seed must be a whole number between 0 and ${SEED_MAX}`)
  }
  return pass(n)
}

function parseOptionalSeed(raw: unknown): ParseResult<number | undefined> {
  if (raw === undefined || raw === null) return pass(undefined)
  if (typeof raw !== 'number' || !Number.isInteger(raw) || raw < 0 || raw > SEED_MAX) {
    return fail(`seed must be a whole number between 0 and ${SEED_MAX}`)
  }
  return pass(raw)
}

function parseOutputFormat(raw: unknown): ParseResult<OutputFormat> {
  if (raw === undefined || raw === null) return pass(DEFAULT_OUTPUT_FORMAT)
  if (typeof raw !== 'string' || !VALID_OUTPUT_FORMATS.has(raw)) {
    return fail(`Unsupported outputFormat: ${String(raw)}`)
  }
  return pass(raw as OutputFormat)
}

function parseNormalization(raw: unknown): ParseResult<TextNormalization | undefined> {
  if (raw === undefined || raw === null) return pass(undefined)
  if (typeof raw !== 'string' || !VALID_NORMALIZATION.has(raw)) {
    return fail(`applyTextNormalization must be one of: ${NORMALIZATION_OPTIONS.join(', ')}`)
  }
  return pass(raw as TextNormalization)
}

/**
 * Fill defaults, clamp every numeric field into range, and drop the parameters
 * the chosen model cannot use. This is the same rule the parameter panel
 * applies when the model changes — enforcing it here means a direct POST
 * cannot send `style` to a model that has no style.
 */
export function resolveVoiceSettings(
  modelId: string,
  partial: Partial<VoiceSettings> | undefined
): VoiceSettings {
  const capabilities = getModelCapabilities(modelId)
  const input = partial ?? {}

  const num = (value: unknown, fallback: number): number =>
    typeof value === 'number' && Number.isFinite(value) ? value : fallback

  const settings: VoiceSettings = {
    stability: clamp(
      num(input.stability, DEFAULT_VOICE_SETTINGS.stability),
      VOICE_SETTING_RANGES.stability.min,
      VOICE_SETTING_RANGES.stability.max
    ),
    similarity_boost: clamp(
      num(input.similarity_boost, DEFAULT_VOICE_SETTINGS.similarity_boost),
      VOICE_SETTING_RANGES.similarity_boost.min,
      VOICE_SETTING_RANGES.similarity_boost.max
    ),
    style: capabilities.style
      ? clamp(
          num(input.style, DEFAULT_VOICE_SETTINGS.style),
          VOICE_SETTING_RANGES.style.min,
          VOICE_SETTING_RANGES.style.max
        )
      : 0,
    use_speaker_boost: capabilities.speakerBoost ? input.use_speaker_boost === true : false,
  }

  if (capabilities.speed && input.speed !== undefined) {
    settings.speed = clamp(
      num(input.speed, 1),
      VOICE_SETTING_RANGES.speed.min,
      VOICE_SETTING_RANGES.speed.max
    )
  }

  return settings
}

// ── Whole-request parsing ───────────────────────────────────────────────────

function asRecord(input: unknown): Record<string, unknown> | null {
  return typeof input === 'object' && input !== null && !Array.isArray(input)
    ? (input as Record<string, unknown>)
    : null
}

export function parseBatchRequest(input: unknown): ParseResult<BatchRequest> {
  const body = asRecord(input)
  if (!body) return fail('Request body must be an object')

  const { rows, voiceId, modelId } = body

  if (!Array.isArray(rows) || rows.length === 0) {
    return fail('No rows provided')
  }
  const parsedRows: BatchRow[] = []
  for (let i = 0; i < rows.length; i++) {
    const row = asRecord(rows[i])
    if (!row || typeof row.text !== 'string' || row.text.trim() === '') {
      return fail(`Row ${i + 1} is missing text`)
    }
    parsedRows.push(row as BatchRow)
  }

  if (typeof voiceId !== 'string' || !voiceId.trim()) return fail('voiceId is required')
  if (typeof modelId !== 'string' || !modelId.trim()) return fail('modelId is required')

  const format = parseOutputFormat(body.outputFormat)
  if (!format.ok) return format
  const seed = parseOptionalSeed(body.seed)
  if (!seed.ok) return seed
  const normalization = parseNormalization(body.applyTextNormalization)
  if (!normalization.ok) return normalization

  return pass({
    rows: parsedRows,
    voiceId: voiceId.trim(),
    modelId: modelId.trim(),
    voiceSettings: resolveVoiceSettings(
      modelId.trim(),
      asRecord(body.voiceSettings) as Partial<VoiceSettings> | null ?? undefined
    ),
    outputFormat: format.value,
    ...(seed.value !== undefined ? { seed: seed.value } : {}),
    ...(normalization.value ? { applyTextNormalization: normalization.value } : {}),
  })
}

export function parseDialogueRequest(input: unknown): ParseResult<DialogueRequest> {
  const body = asRecord(input)
  if (!body) return fail('Request body must be an object')

  const { modelId, inputs } = body

  if (typeof modelId !== 'string' || !modelId.trim()) return fail('modelId is required')
  if (!getModelCapabilities(modelId.trim()).dialogue) {
    return fail(`Model ${modelId} does not support Text-to-Dialogue`)
  }

  if (!Array.isArray(inputs) || inputs.length === 0) {
    return fail('At least one input row is required')
  }
  if (inputs.length > DIALOGUE_LIMITS.maxLines) {
    return fail(`Maximum ${DIALOGUE_LIMITS.maxLines} dialogue lines supported`)
  }

  const parsedInputs: DialogueInput[] = []
  for (const raw of inputs) {
    const line = asRecord(raw)
    if (
      !line ||
      typeof line.voiceId !== 'string' ||
      !line.voiceId.trim() ||
      typeof line.text !== 'string' ||
      !line.text.trim()
    ) {
      return fail('Each input requires a voiceId and non-empty text')
    }
    parsedInputs.push({ voiceId: line.voiceId.trim(), text: line.text })
  }

  const uniqueVoices = new Set(parsedInputs.map((i) => i.voiceId))
  if (uniqueVoices.size > DIALOGUE_LIMITS.maxUniqueVoices) {
    return fail(`Maximum ${DIALOGUE_LIMITS.maxUniqueVoices} unique voices supported`)
  }

  const totalChars = parsedInputs.reduce((sum, i) => sum + i.text.length, 0)
  if (totalChars > DIALOGUE_LIMITS.maxTotalChars) {
    return fail(
      `Total characters must be ≤ ${DIALOGUE_LIMITS.maxTotalChars} (got ${totalChars})`
    )
  }

  const format = parseOutputFormat(body.outputFormat)
  if (!format.ok) return format
  const seed = parseOptionalSeed(body.seed)
  if (!seed.ok) return seed
  const normalization = parseNormalization(body.applyTextNormalization)
  if (!normalization.ok) return normalization

  const stability =
    typeof body.stability === 'number' && Number.isFinite(body.stability)
      ? clamp(body.stability, VOICE_SETTING_RANGES.stability.min, VOICE_SETTING_RANGES.stability.max)
      : DEFAULT_STABILITY

  return pass({
    modelId: modelId.trim(),
    inputs: parsedInputs,
    stability,
    outputFormat: format.value,
    ...(typeof body.filename === 'string' && body.filename.trim()
      ? { filename: body.filename.trim() }
      : {}),
    ...(seed.value !== undefined ? { seed: seed.value } : {}),
    ...(normalization.value ? { applyTextNormalization: normalization.value } : {}),
    ...(typeof body.languageCode === 'string' && body.languageCode.trim()
      ? { languageCode: body.languageCode.trim() }
      : {}),
  })
}
