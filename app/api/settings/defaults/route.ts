import { NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { getUserSettings, updateUserSettings } from '@/lib/supabase/user-settings'

export const runtime = 'edge'

export async function GET() {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const settings = await getUserSettings(userId)
    return NextResponse.json(settings)
  } catch (error) {
    console.error('Error fetching user settings:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch settings' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { default_translation_model, default_enhancement_model } = body

    const updates: {
      default_translation_model?: string
      default_enhancement_model?: string
    } = {}

    if (default_translation_model !== undefined) {
      updates.default_translation_model = default_translation_model
    }

    if (default_enhancement_model !== undefined) {
      updates.default_enhancement_model = default_enhancement_model
    }

    const settings = await updateUserSettings(userId, updates)
    return NextResponse.json(settings)
  } catch (error) {
    console.error('Error updating user settings:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to update settings' },
      { status: 500 }
    )
  }
}
