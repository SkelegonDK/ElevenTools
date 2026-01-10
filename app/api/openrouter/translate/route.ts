import { NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { getApiKey } from '@/lib/supabase/api-keys'
import { translate } from '@/lib/openrouter/api'

export const runtime = 'edge'

export async function POST(request: Request) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const apiKey = await getApiKey(userId, 'openrouter')

    if (!apiKey) {
      return NextResponse.json(
        { error: 'OpenRouter API key not configured' },
        { status: 400 }
      )
    }

    const body = await request.json()
    const { text, targetLanguage, model }: {
      text: string
      targetLanguage: string
      model?: string
    } = body

    if (!text || !targetLanguage) {
      return NextResponse.json(
        { error: 'Missing required parameters: text and targetLanguage' },
        { status: 400 }
      )
    }

    const translatedText = await translate({
      apiKey,
      text,
      targetLanguage,
      model,
    })

    return NextResponse.json({ translatedText })
  } catch (error) {
    console.error('Error translating text:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to translate text' },
      { status: 500 }
    )
  }
}
