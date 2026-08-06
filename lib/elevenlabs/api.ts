import 'server-only'
import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js'
import { revalidateTag, unstable_cache } from 'next/cache'
import {
  DEFAULT_OUTPUT_FORMAT,
  type DialogueInput,
  type ElevenLabsModel,
  type ElevenLabsVoice,
  type OutputFormat,
  type TextNormalization,
  type VoiceSettings,
} from './types'

export const VOICES_CACHE_TAG = 'elevenlabs:voices'
export const MODELS_CACHE_TAG = 'elevenlabs:models'

export {
  DEFAULT_OUTPUT_FORMAT,
  extensionForOutputFormat,
} from './types'
export type {
  DialogueInput,
  ElevenLabsModel,
  ElevenLabsVoice,
  OutputFormat,
  TextNormalization,
  VoiceSettings,
} from './types'

export interface GenerateAudioParams {
  apiKey: string
  voiceId: string
  modelId: string
  text: string
  voiceSettings: VoiceSettings
  languageCode?: string
  outputFormat?: OutputFormat
  seed?: number
  applyTextNormalization?: TextNormalization
  previousText?: string
  nextText?: string
  previousRequestIds?: string[]
  nextRequestIds?: string[]
}

export interface GenerateAudioResult {
  audio: ArrayBuffer
  requestId: string | null
  outputFormat: OutputFormat
}

export interface GenerateDialogueParams {
  apiKey: string
  modelId: string
  inputs: DialogueInput[]
  stability?: number
  seed?: number
  outputFormat?: OutputFormat
  applyTextNormalization?: TextNormalization
  languageCode?: string
}

function client(apiKey: string): ElevenLabsClient {
  return new ElevenLabsClient({ apiKey })
}

async function streamToArrayBuffer(stream: ReadableStream<Uint8Array>): Promise<ArrayBuffer> {
  const reader = stream.getReader()
  const chunks: Uint8Array[] = []
  let total = 0
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    if (value) {
      chunks.push(value)
      total += value.length
    }
  }
  const out = new Uint8Array(total)
  let offset = 0
  for (const c of chunks) {
    out.set(c, offset)
    offset += c.length
  }
  return out.buffer
}

export async function fetchModels(apiKey: string): Promise<ElevenLabsModel[]> {
  const models = await client(apiKey).models.list()
  return models
    .filter((m) => m.canDoTextToSpeech !== false)
    .map((m) => ({ model_id: m.modelId, name: m.name ?? m.modelId }))
}

export async function fetchVoices(apiKey: string): Promise<ElevenLabsVoice[]> {
  const result = await client(apiKey).voices.search()
  const list = result.voices ?? []
  return list.map((v) => ({ voice_id: v.voiceId, name: v.name ?? 'Unnamed voice' }))
}

export async function fetchVoiceById(
  apiKey: string,
  voiceId: string
): Promise<ElevenLabsVoice | null> {
  try {
    const voice = await client(apiKey).voices.get(voiceId)
    return { voice_id: voice.voiceId ?? voiceId, name: voice.name ?? 'Unknown Voice' }
  } catch {
    return null
  }
}

function requireApiKey(): string {
  const k = process.env.ELEVENLABS_API_KEY?.trim()
  if (!k) throw new Error('ELEVENLABS_API_KEY not set in .env.local')
  return k
}

/**
 * How fresh a catalogue resource has to be, declared once.
 *
 * `browserMaxAge` is how long a client may reuse its copy without asking;
 * `serverRevalidate` is how long the server cache holds one, and it doubles as
 * the `stale-while-revalidate` budget — the browser may serve a stale copy for
 * exactly as long as the server would still be sitting on one.
 */
interface Freshness {
  browserMaxAge: number
  serverRevalidate: number
}

const VOICES_FRESHNESS: Freshness = { browserMaxAge: 600, serverRevalidate: 1800 }
const MODELS_FRESHNESS: Freshness = { browserMaxAge: 600, serverRevalidate: 3600 }

export function cacheControl(freshness: Freshness): string {
  return `private, max-age=${freshness.browserMaxAge}, stale-while-revalidate=${freshness.serverRevalidate}`
}

export const VOICES_CACHE_CONTROL = cacheControl(VOICES_FRESHNESS)
export const MODELS_CACHE_CONTROL = cacheControl(MODELS_FRESHNESS)

// Cached env-aware wrappers used by route handlers and Server Components.
// The unstable_cache layer keys on the static key parts only — the apiKey is
// read from env at execution time and is never embedded in the cache key.
export const getVoices = unstable_cache(
  async (): Promise<ElevenLabsVoice[]> => fetchVoices(requireApiKey()),
  ['elevenlabs', 'voices', 'v1'],
  { revalidate: VOICES_FRESHNESS.serverRevalidate, tags: [VOICES_CACHE_TAG] }
)

export const getModels = unstable_cache(
  async (): Promise<ElevenLabsModel[]> => fetchModels(requireApiKey()),
  ['elevenlabs', 'models', 'v1'],
  { revalidate: MODELS_FRESHNESS.serverRevalidate, tags: [MODELS_CACHE_TAG] }
)

/**
 * A single voice is not held in the server cache, so it only advertises the
 * browser window — no `stale-while-revalidate` promise the server cannot keep.
 */
export const VOICE_DETAIL_CACHE_CONTROL = `private, max-age=${VOICES_FRESHNESS.browserMaxAge}`

export function revalidateVoices(): void {
  revalidateTag(VOICES_CACHE_TAG)
}

export function revalidateModels(): void {
  revalidateTag(MODELS_CACHE_TAG)
}

export async function generateAudio(params: GenerateAudioParams): Promise<GenerateAudioResult> {
  const {
    apiKey,
    voiceId,
    modelId,
    text,
    voiceSettings,
    languageCode,
    outputFormat = DEFAULT_OUTPUT_FORMAT,
    seed,
    applyTextNormalization,
    previousText,
    nextText,
    previousRequestIds,
    nextRequestIds,
  } = params

  const c = client(apiKey)
  const { data: stream, rawResponse } = await c.textToSpeech
    .convert(voiceId, {
      text,
      modelId,
      outputFormat,
      voiceSettings: {
        stability: voiceSettings.stability,
        similarityBoost: voiceSettings.similarity_boost,
        style: voiceSettings.style,
        useSpeakerBoost: voiceSettings.use_speaker_boost,
        ...(voiceSettings.speed !== undefined ? { speed: voiceSettings.speed } : {}),
      },
      ...(languageCode ? { languageCode } : {}),
      ...(seed !== undefined ? { seed } : {}),
      ...(applyTextNormalization ? { applyTextNormalization } : {}),
      ...(previousText ? { previousText } : {}),
      ...(nextText ? { nextText } : {}),
      ...(previousRequestIds && previousRequestIds.length
        ? { previousRequestIds: previousRequestIds.slice(-3) }
        : {}),
      ...(nextRequestIds && nextRequestIds.length
        ? { nextRequestIds: nextRequestIds.slice(0, 3) }
        : {}),
    })
    .withRawResponse()

  const audio = await streamToArrayBuffer(stream)
  const requestId =
    rawResponse.headers?.get?.('request-id') ?? rawResponse.headers?.get?.('Request-Id') ?? null
  return { audio, requestId, outputFormat }
}

export async function generateDialogue(
  params: GenerateDialogueParams
): Promise<GenerateAudioResult> {
  const {
    apiKey,
    modelId,
    inputs,
    stability,
    seed,
    outputFormat = DEFAULT_OUTPUT_FORMAT,
    applyTextNormalization,
    languageCode,
  } = params

  const c = client(apiKey)
  const { data: stream, rawResponse } = await c.textToDialogue
    .convert({
      modelId,
      outputFormat,
      inputs: inputs.map((i) => ({ voiceId: i.voiceId, text: i.text })),
      ...(stability !== undefined ? { settings: { stability } } : {}),
      ...(seed !== undefined ? { seed } : {}),
      ...(applyTextNormalization ? { applyTextNormalization } : {}),
      ...(languageCode ? { languageCode } : {}),
    })
    .withRawResponse()

  const audio = await streamToArrayBuffer(stream)
  const requestId =
    rawResponse.headers?.get?.('request-id') ?? rawResponse.headers?.get?.('Request-Id') ?? null
  return { audio, requestId, outputFormat }
}
