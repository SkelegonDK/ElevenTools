import { NextResponse } from 'next/server'
import { fetchVoiceById, VOICE_DETAIL_CACHE_CONTROL } from '@/lib/elevenlabs/api'

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ voiceId: string }> }
) {
  try {
    const apiKey = process.env.ELEVENLABS_API_KEY?.trim()
    if (!apiKey) {
      return NextResponse.json(
        { error: 'ELEVENLABS_API_KEY not set in .env.local' },
        { status: 400 }
      )
    }

    const { voiceId } = await params
    if (!voiceId) {
      return NextResponse.json({ error: 'Voice ID is required' }, { status: 400 })
    }

    const voice = await fetchVoiceById(apiKey, voiceId)
    if (!voice) {
      return NextResponse.json({ error: 'Voice not found' }, { status: 404 })
    }

    return NextResponse.json(
      { voice },
      { headers: { 'Cache-Control': VOICE_DETAIL_CACHE_CONTROL } }
    )
  } catch (error) {
    console.error('Error fetching voice:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch voice' },
      { status: 500 }
    )
  }
}
