import { NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { getApiKey } from '@/lib/supabase/api-keys'
import { fetchModels, filterFreeModels, searchModelsFuzzy } from '@/lib/openrouter/api'

export const runtime = 'edge'

export async function GET(request: Request) {
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

    const { searchParams } = new URL(request.url)
    const freeOnly = searchParams.get('freeOnly') === 'true'
    const searchQuery = searchParams.get('search') || ''

    let models = await fetchModels(apiKey)

    // Apply filters
    if (freeOnly) {
      models = filterFreeModels(models)
    }

    if (searchQuery) {
      models = searchModelsFuzzy(models, searchQuery)
    }

    return NextResponse.json({ models })
  } catch (error) {
    console.error('Error fetching OpenRouter models:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch models' },
      { status: 500 }
    )
  }
}
