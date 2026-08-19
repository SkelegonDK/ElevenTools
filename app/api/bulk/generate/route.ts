import { NextResponse } from 'next/server'
import { runBatch } from '@/lib/generation/batch'
import { createGenerationPorts, readApiKey } from '@/lib/generation/ports'
import { parseBatchRequest } from '@/lib/generation/request'

export async function POST(request: Request) {
  try {
    const apiKey = readApiKey()
    if (!apiKey) {
      return NextResponse.json(
        { error: 'ELEVENLABS_API_KEY not set in .env.local' },
        { status: 400 }
      )
    }

    const parsed = parseBatchRequest(await request.json())
    if (!parsed.ok) {
      return NextResponse.json({ error: parsed.error }, { status: 400 })
    }

    return NextResponse.json(await runBatch(parsed.value, createGenerationPorts(apiKey)))
  } catch (error) {
    console.error('Error in bulk generation:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to generate audio' },
      { status: 500 }
    )
  }
}
