import { NextResponse } from 'next/server'
import { getVoices, VOICES_CACHE_CONTROL } from '@/lib/elevenlabs/api'

export async function GET() {
  try {
    const voices = await getVoices()
    return NextResponse.json({ voices }, { headers: { 'Cache-Control': VOICES_CACHE_CONTROL } })
  } catch (error) {
    console.error('Error fetching voices:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch voices' },
      { status: 500 }
    )
  }
}
