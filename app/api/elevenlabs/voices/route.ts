import { NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { getApiKey } from '@/lib/supabase/api-keys'
import { fetchVoices } from '@/lib/elevenlabs/api'

export const runtime = 'edge'

export async function GET() {
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

    const voices = await fetchVoices(apiKey)

    return NextResponse.json({ voices })
  } catch (error) {
    console.error('Error fetching voices:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch voices' },
      { status: 500 }
    )
  }
}
