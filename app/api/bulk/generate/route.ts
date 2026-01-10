import { NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { getApiKey } from '@/lib/supabase/api-keys'
import { generateAudio, type VoiceSettings } from '@/lib/elevenlabs/api'
import { supabaseAdmin } from '@/lib/supabase/admin'
import { replaceVariables } from '@/lib/utils/csv'

export const runtime = 'edge'

export async function POST(request: Request) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const apiKey = await getApiKey(userId, 'elevenlabs')

    if (!apiKey) {
      return NextResponse.json(
        { error: 'ElevenLabs API key not configured' },
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
      return NextResponse.json(
        { error: 'No rows provided' },
        { status: 400 }
      )
    }

    if (!voiceId || !modelId || !voiceSettings) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      )
    }

    // Get user ID from Supabase
    const { data: user } = await supabaseAdmin
      .from('users')
      .select('id')
      .eq('clerk_id', userId)
      .single()

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    const results = []
    const errors = []

    // Process rows sequentially to avoid rate limits
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i]
      try {
        // Replace variables in text
        const processedText = replaceVariables(row.text, row)

        // Generate filename if not provided
        let filename = row.filename || `audio_${i + 1}.mp3`
        filename = replaceVariables(filename, row)
        if (!filename.endsWith('.mp3')) {
          filename += '.mp3'
        }

        // Generate audio
        const audioBuffer = await generateAudio({
          apiKey,
          voiceId,
          modelId,
          text: processedText,
          voiceSettings,
        })

        // Upload to Supabase Storage using admin client
        const storagePath = `${userId}/bulk/${batchId}/${filename}`
        const { data: uploadData, error: uploadError } = await supabaseAdmin.storage
          .from('audio-files')
          .upload(storagePath, audioBuffer, {
            contentType: 'audio/mpeg',
            upsert: false,
          })

        if (uploadError || !uploadData) {
          throw new Error(`Failed to upload: ${uploadError?.message}`)
        }

        // Get public URL
        const { data: urlData } = supabaseAdmin.storage
          .from('audio-files')
          .getPublicUrl(storagePath)

        // Save generation to database
        await supabaseAdmin.from('generations').insert({
          user_id: user.id,
          batch_id: batchId,
          text: processedText,
          voice_id: voiceId,
          model_id: modelId,
          blob_url: urlData.publicUrl,
          filename,
        })

        results.push({
          index: i,
          filename,
          url: urlData.publicUrl,
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
