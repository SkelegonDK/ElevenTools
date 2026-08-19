import { NextResponse } from 'next/server'
import { fetchModels, filterFreeModels, searchModelsFuzzy } from '@/lib/openrouter/api'

export async function GET(request: Request) {
  try {
    const apiKey = process.env.OPENROUTER_API_KEY?.trim()
    if (!apiKey) {
      return NextResponse.json(
        { error: 'OPENROUTER_API_KEY not set in .env.local' },
        { status: 400 }
      )
    }

    const { searchParams } = new URL(request.url)
    const freeOnly = searchParams.get('freeOnly') === 'true'
    const searchQuery = searchParams.get('search') || ''

    let models = await fetchModels(apiKey)
    if (freeOnly) models = filterFreeModels(models)
    if (searchQuery) models = searchModelsFuzzy(models, searchQuery)

    return NextResponse.json({ models })
  } catch (error) {
    console.error('Error fetching OpenRouter models:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch models' },
      { status: 500 }
    )
  }
}
