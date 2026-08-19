import { NextResponse } from 'next/server'
import { translate } from '@/lib/openrouter/api'

export async function POST(request: Request) {
  try {
    const apiKey = process.env.OPENROUTER_API_KEY?.trim()
    if (!apiKey) {
      return NextResponse.json(
        { error: 'OPENROUTER_API_KEY not set in .env.local' },
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

    const translatedText = await translate({ apiKey, text, targetLanguage, model })
    return NextResponse.json({ translatedText })
  } catch (error) {
    console.error('Error translating text:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to translate text' },
      { status: 500 }
    )
  }
}
