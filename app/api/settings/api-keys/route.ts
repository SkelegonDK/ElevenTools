import { NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { saveApiKey } from '@/lib/supabase/api-keys'

export const runtime = 'edge'

export async function POST(request: Request) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { service, apiKey }: { service: 'elevenlabs' | 'openrouter'; apiKey: string } = body

    if (!service || !apiKey) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      )
    }

    if (service !== 'elevenlabs' && service !== 'openrouter') {
      return NextResponse.json(
        { error: 'Invalid service. Must be "elevenlabs" or "openrouter"' },
        { status: 400 }
      )
    }

    await saveApiKey(userId, service, apiKey)

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Error saving API key:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to save API key' },
      { status: 500 }
    )
  }
}
