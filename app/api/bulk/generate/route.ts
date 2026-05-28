import { NextResponse } from 'next/server'
import { randomUUID } from 'node:crypto'
import { generateAudio, type VoiceSettings } from '@/lib/elevenlabs/api'
import { replaceVariables } from '@/lib/utils/csv'
import { insertGeneration } from '@/lib/db'
import { saveAudio } from '@/lib/storage'

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
    }: {
      rows: Array<{ text: string; filename?: string; [key: string]: any }>
      voiceId: string
      modelId: string
      voiceSettings: VoiceSettings
      batchId: string
    } = body

    if (!rows || !Array.isArray(rows) || rows.length === 0) {
      return NextResponse.json({ error: 'No rows provided' }, { status: 400 })
    }

    if (!voiceId || !modelId || !voiceSettings || !batchId) {
      return NextResponse.json({ error: 'Missing required parameters' }, { status: 400 })
    }

    const results = []
    const errors = []

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i]
      try {
        const processedText = replaceVariables(row.text, row)

        let filename = row.filename || `audio_${i + 1}.mp3`
        filename = replaceVariables(filename, row)
        if (!filename.endsWith('.mp3')) {
          filename += '.mp3'
        }

        const audioBuffer = await generateAudio({
          apiKey,
          voiceId,
          modelId,
          text: processedText,
          voiceSettings,
        })

        const audioPath = saveAudio(batchId, filename, audioBuffer)

        const id = randomUUID()
        insertGeneration({
          id,
          batch_id: batchId,
          text: processedText,
          voice_id: voiceId,
          model_id: modelId,
          audio_path: audioPath,
          filename,
        })

        results.push({
          index: i,
          filename,
          url: audioPath,
          text: processedText,
        })
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
