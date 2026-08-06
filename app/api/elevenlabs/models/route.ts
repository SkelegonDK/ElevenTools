import { NextResponse } from 'next/server'
import { getModels, MODELS_CACHE_CONTROL } from '@/lib/elevenlabs/api'

export async function GET() {
  try {
    const models = await getModels()
    return NextResponse.json({ models }, { headers: { 'Cache-Control': MODELS_CACHE_CONTROL } })
  } catch (error) {
    console.error('Error fetching models:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch models' },
      { status: 500 }
    )
  }
}
