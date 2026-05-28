import { NextResponse } from 'next/server'
import { fetchVoices } from '@/lib/elevenlabs/api'

export async function GET() {
  try {
    const apiKey = process.env.ELEVENLABS_API_KEY?.trim()
    if (!apiKey) {
      return NextResponse.json(
        { error: 'ELEVENLABS_API_KEY not set in .env.local' },
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
