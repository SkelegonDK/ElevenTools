import { NextResponse } from 'next/server'
import { randomUUID } from 'node:crypto'
import { generateDialogue } from '@/lib/elevenlabs/api'
import {
  DEFAULT_OUTPUT_FORMAT,
  extensionForOutputFormat,
  type DialogueInput,
  type OutputFormat,
  type TextNormalization,
} from '@/lib/elevenlabs/types'
import { insertGeneration } from '@/lib/db'
import { saveAudio } from '@/lib/storage'

const MAX_UNIQUE_VOICES = 10
const MAX_TOTAL_CHARS = 2000
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
      modelId,
      inputs,
      stability,
      seed,
      outputFormat,
      applyTextNormalization,
      languageCode,
      filename,
    }: {
      modelId: string
      inputs: DialogueInput[]
      stability?: number
      seed?: number
      outputFormat?: OutputFormat
      applyTextNormalization?: TextNormalization
      languageCode?: string
      filename?: string
    } = body

    if (!modelId) {
      return NextResponse.json({ error: 'modelId is required' }, { status: 400 })
    }
    if (!Array.isArray(inputs) || inputs.length === 0) {
      return NextResponse.json({ error: 'At least one input row is required' }, { status: 400 })
    }
    for (const inp of inputs) {
      if (!inp?.voiceId || !inp?.text?.trim()) {
        return NextResponse.json(
          { error: 'Each input requires a voiceId and non-empty text' },
          { status: 400 }
        )
      }
    }
    const uniqueVoices = new Set(inputs.map((i) => i.voiceId))
    if (uniqueVoices.size > MAX_UNIQUE_VOICES) {
      return NextResponse.json(
        { error: `Maximum ${MAX_UNIQUE_VOICES} unique voices supported` },
        { status: 400 }
      )
    }
    const totalChars = inputs.reduce((sum, i) => sum + i.text.length, 0)
    if (totalChars > MAX_TOTAL_CHARS) {
      return NextResponse.json(
        { error: `Total characters must be ≤ ${MAX_TOTAL_CHARS} (got ${totalChars})` },
        { status: 400 }
      )
    }

    const resolvedFormat: OutputFormat = outputFormat ?? DEFAULT_OUTPUT_FORMAT
    const ext = extensionForOutputFormat(resolvedFormat)
    const normalization =
      applyTextNormalization && VALID_NORMALIZATION.has(applyTextNormalization)
        ? applyTextNormalization
        : undefined

    const id = randomUUID()
    const batchId = `dialogue-${id.slice(0, 8)}`
    const safeFilename = sanitiseFilename(filename) || `dialogue.${ext}`

    const { audio, requestId } = await generateDialogue({
      apiKey,
      modelId,
      inputs,
      ...(stability !== undefined ? { stability } : {}),
      ...(seed !== undefined ? { seed } : {}),
      ...(normalization ? { applyTextNormalization: normalization } : {}),
      ...(languageCode ? { languageCode } : {}),
      outputFormat: resolvedFormat,
    })

    const audioPath = saveAudio(batchId, safeFilename, audio)

    const combinedText = inputs.map((i) => `[${i.voiceId}] ${i.text}`).join('\n')
    insertGeneration({
      id,
      batch_id: batchId,
      text: combinedText,
      voice_id: inputs[0].voiceId,
      model_id: modelId,
      audio_path: audioPath,
      filename: safeFilename,
      request_id: requestId,
      seed: seed ?? null,
      output_format: resolvedFormat,
      kind: 'dialogue',
    })

    return NextResponse.json({
      id,
      batchId,
      url: audioPath,
      filename: safeFilename,
      requestId,
      outputFormat: resolvedFormat,
    })
  } catch (error) {
    console.error('Error in dialogue generation:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to generate dialogue' },
      { status: 500 }
    )
  }
}

function sanitiseFilename(name: string | undefined): string | null {
  if (!name) return null
  const cleaned = name.replace(/[^a-zA-Z0-9._-]/g, '_').trim()
  return cleaned || null
}
