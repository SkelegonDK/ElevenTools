/**
 * The batch run: filename derivation, prosody continuity, the request-id ring
 * buffer, per-row error accumulation, and the order of the write-then-persist
 * pair.
 *
 * Every dependency arrives through `GenerationPorts`, so this module is a
 * value-in / value-out function. The production adapter wires the SDK, the
 * audio store and SQLite; the tests wire in-memory equivalents. No HTTP, no
 * filesystem, no database appears below.
 */

import { extensionForOutputFormat, type OutputFormat } from '@/lib/elevenlabs/types'
import { replaceVariables } from '@/lib/utils/csv'
import type { BatchRequest, BatchRow, DialogueRequest } from './request'

/** How many recent request ids ElevenLabs will accept for prosody stitching. */
const REQUEST_ID_WINDOW = 3

export interface GenerateCall {
  voiceId: string
  modelId: string
  text: string
  voiceSettings: BatchRequest['voiceSettings']
  outputFormat: OutputFormat
  seed?: number
  applyTextNormalization?: BatchRequest['applyTextNormalization']
  previousText?: string
  nextText?: string
  previousRequestIds?: string[]
}

export interface DialogueCall {
  modelId: string
  inputs: DialogueRequest['inputs']
  stability: number
  outputFormat: OutputFormat
  seed?: number
  applyTextNormalization?: DialogueRequest['applyTextNormalization']
  languageCode?: string
}

export interface GeneratedAudio {
  audio: ArrayBuffer
  requestId: string | null
}

export interface StoredAudioRef {
  filename: string
  url: string
}

export interface PersistedRow {
  id: string
  batch_id: string
  text: string
  voice_id: string
  model_id: string
  audio_path: string
  filename: string
  request_id: string | null
  seed: number | null
  output_format: string
  kind: 'tts' | 'dialogue'
}

export interface GenerationPorts {
  generateAudio(call: GenerateCall): Promise<GeneratedAudio>
  generateDialogue(call: DialogueCall): Promise<GeneratedAudio>
  newBatchId(prefix: string): string
  newGenerationId(): string
  save(batchId: string, name: string, ext: string, bytes: ArrayBuffer): StoredAudioRef
  persist(row: PersistedRow): void
}

export interface BatchRowResult {
  index: number
  filename: string
  url: string
  text: string
}

export interface BatchRowError {
  index: number
  error: string
}

export interface BatchResult {
  batchId: string
  success: number
  failed: number
  results: BatchRowResult[]
  errors: BatchRowError[]
}

/**
 * The name a row wants, before the store applies the output format's
 * extension. Variables in the template are substituted from the row itself,
 * so `hi_{firstName}` follows the same rules as the row's text.
 */
export function deriveName(row: BatchRow, index: number): string {
  const template = row.filename?.trim() || `audio_${index + 1}`
  return replaceVariables(template, row as Record<string, string>)
}

export async function runBatch(
  request: BatchRequest,
  ports: GenerationPorts
): Promise<BatchResult> {
  const batchId = ports.newBatchId('batch')
  const ext = extensionForOutputFormat(request.outputFormat)

  // Resolve every row's text up front so each call can carry its neighbours'
  // text for prosody continuity.
  const rows = request.rows.map((row, index) => ({
    row,
    text: replaceVariables(row.text, row as Record<string, string>),
    name: deriveName(row, index),
  }))

  const results: BatchRowResult[] = []
  const errors: BatchRowError[] = []
  const recentRequestIds: string[] = []

  for (let i = 0; i < rows.length; i++) {
    const { text, name } = rows[i]
    try {
      const { audio, requestId } = await ports.generateAudio({
        voiceId: request.voiceId,
        modelId: request.modelId,
        text,
        voiceSettings: request.voiceSettings,
        outputFormat: request.outputFormat,
        ...(request.seed !== undefined ? { seed: request.seed } : {}),
        ...(request.applyTextNormalization
          ? { applyTextNormalization: request.applyTextNormalization }
          : {}),
        ...(i > 0 ? { previousText: rows[i - 1].text } : {}),
        ...(i < rows.length - 1 ? { nextText: rows[i + 1].text } : {}),
        ...(recentRequestIds.length ? { previousRequestIds: [...recentRequestIds] } : {}),
      })

      const stored = ports.save(batchId, name, ext, audio)

      ports.persist({
        id: ports.newGenerationId(),
        batch_id: batchId,
        text,
        voice_id: request.voiceId,
        model_id: request.modelId,
        audio_path: stored.url,
        filename: stored.filename,
        request_id: requestId,
        seed: request.seed ?? null,
        output_format: request.outputFormat,
        kind: 'tts',
      })

      if (requestId) {
        recentRequestIds.push(requestId)
        if (recentRequestIds.length > REQUEST_ID_WINDOW) recentRequestIds.shift()
      }

      results.push({ index: i, filename: stored.filename, url: stored.url, text })
    } catch (error) {
      errors.push({
        index: i,
        error: error instanceof Error ? error.message : 'Unknown error',
      })
    }
  }

  return { batchId, success: results.length, failed: errors.length, results, errors }
}

export interface DialogueResult {
  id: string
  batchId: string
  url: string
  filename: string
  requestId: string | null
  outputFormat: OutputFormat
}

export async function runDialogue(
  request: DialogueRequest,
  ports: GenerationPorts
): Promise<DialogueResult> {
  const batchId = ports.newBatchId('dialogue')
  const ext = extensionForOutputFormat(request.outputFormat)

  const { audio, requestId } = await ports.generateDialogue({
    modelId: request.modelId,
    inputs: request.inputs,
    stability: request.stability,
    outputFormat: request.outputFormat,
    ...(request.seed !== undefined ? { seed: request.seed } : {}),
    ...(request.applyTextNormalization
      ? { applyTextNormalization: request.applyTextNormalization }
      : {}),
    ...(request.languageCode ? { languageCode: request.languageCode } : {}),
  })

  const stored = ports.save(batchId, request.filename ?? 'dialogue', ext, audio)
  const id = ports.newGenerationId()

  ports.persist({
    id,
    batch_id: batchId,
    text: request.inputs.map((i) => `[${i.voiceId}] ${i.text}`).join('\n'),
    voice_id: request.inputs[0].voiceId,
    model_id: request.modelId,
    audio_path: stored.url,
    filename: stored.filename,
    request_id: requestId,
    seed: request.seed ?? null,
    output_format: request.outputFormat,
    kind: 'dialogue',
  })

  return {
    id,
    batchId,
    url: stored.url,
    filename: stored.filename,
    requestId,
    outputFormat: request.outputFormat,
  }
}
