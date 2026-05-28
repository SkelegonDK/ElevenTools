import { NextResponse } from 'next/server'
import { randomUUID } from 'node:crypto'
import { generateAudio } from '@/lib/elevenlabs/api'
import {
  DEFAULT_OUTPUT_FORMAT,
  extensionForOutputFormat,
  type OutputFormat,
  type TextNormalization,
  type VoiceSettings,
} from '@/lib/elevenlabs/types'
import { replaceVariables } from '@/lib/utils/csv'
import { insertGeneration } from '@/lib/db'
import { saveAudio } from '@/lib/storage'

const VALID_NORMALIZATION = new Set(['auto', 'on', 'off'])

export async function POST(request: Request) {
  try {
    const apiKey = process.env.ELEVENLABS_API_KEY?.trim()
    if (!apiKey) {
      return NextResponse.json(
        { error: 'ELEVENLABS_API_KEY not set in .env.local' },
        { status: 400 }
      )
    }

    const body = await request.json()
    const {
      rows,
      voiceId,
      modelId,
      voiceSettings,
      batchId,
      outputFormat,
      seed,
      applyTextNormalization,
    }: {
      rows: Array<{ text: string; filename?: string; [key: string]: any }>
      voiceId: string
      modelId: string
      voiceSettings: VoiceSettings
      batchId: string
      outputFormat?: OutputFormat
      seed?: number
      applyTextNormalization?: TextNormalization
    } = body

    if (!rows || !Array.isArray(rows) || rows.length === 0) {
      return NextResponse.json({ error: 'No rows provided' }, { status: 400 })
    }

    if (!voiceId || !modelId || !voiceSettings || !batchId) {
      return NextResponse.json({ error: 'Missing required parameters' }, { status: 400 })
    }

    const resolvedFormat: OutputFormat = outputFormat ?? DEFAULT_OUTPUT_FORMAT
    const ext = extensionForOutputFormat(resolvedFormat)
    const normalization =
      applyTextNormalization && VALID_NORMALIZATION.has(applyTextNormalization)
        ? applyTextNormalization
        : undefined

    const results: Array<{ index: number; filename: string; url: string; text: string }> = []
    const errors: Array<{ index: number; error: string }> = []

    // Pre-resolve text for every row so we can pass previousText / nextText
    // around for prosody continuity.
    const processedRows = rows.map((row, i) => ({
      original: row,
      text: replaceVariables(row.text, row),
      filename: deriveFilename(row, i, ext),
    }))

    // Rolling buffer of the last 3 request_ids — fed back as previousRequestIds
    // to keep prosody continuous across the batch.
    const recentRequestIds: string[] = []

    for (let i = 0; i < processedRows.length; i++) {
      const { text, filename } = processedRows[i]
      try {
        const { audio, requestId } = await generateAudio({
          apiKey,
          voiceId,
          modelId,
          text,
          voiceSettings,
          outputFormat: resolvedFormat,
          ...(seed !== undefined ? { seed } : {}),
          ...(normalization ? { applyTextNormalization: normalization } : {}),
          ...(i > 0 ? { previousText: processedRows[i - 1].text } : {}),
          ...(i < processedRows.length - 1 ? { nextText: processedRows[i + 1].text } : {}),
          ...(recentRequestIds.length ? { previousRequestIds: [...recentRequestIds] } : {}),
        })

        const audioPath = saveAudio(batchId, filename, audio)

        const id = randomUUID()
        insertGeneration({
          id,
          batch_id: batchId,
          text,
          voice_id: voiceId,
          model_id: modelId,
          audio_path: audioPath,
          filename,
          request_id: requestId,
          seed: seed ?? null,
          output_format: resolvedFormat,
          kind: 'tts',
        })

        if (requestId) {
          recentRequestIds.push(requestId)
          if (recentRequestIds.length > 3) recentRequestIds.shift()
        }

        results.push({ index: i, filename, url: audioPath, text })
      } catch (error) {
        errors.push({
          index: i,
          error: error instanceof Error ? error.message : 'Unknown error',
        })
      }
    }

    return NextResponse.json({
      success: results.length,
      failed: errors.length,
      results,
      errors,
    })
  } catch (error) {
    console.error('Error in bulk generation:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to generate audio' },
      { status: 500 }
    )
  }
}

function deriveFilename(
  row: { text: string; filename?: string; [key: string]: any },
  index: number,
  ext: string
): string {
  let filename = row.filename || `audio_${index + 1}.${ext}`
  filename = replaceVariables(filename, row)
  // Strip a trailing dotted extension if it differs from the chosen output
  // format, then re-apply the correct one.
  if (!filename.toLowerCase().endsWith(`.${ext}`)) {
    filename = filename.replace(/\.[a-z0-9]{1,5}$/i, '')
    filename += `.${ext}`
  }
  return filename
}
