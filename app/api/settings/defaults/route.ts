import { NextResponse } from 'next/server'
import { getSettings, updateSettings } from '@/lib/db'

export async function GET() {
  try {
    return NextResponse.json(getSettings())
  } catch (error) {
    console.error('Error fetching settings:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch settings' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { default_translation_model, default_enhancement_model } = body

    const settings = updateSettings({
      ...(default_translation_model !== undefined && { default_translation_model }),
      ...(default_enhancement_model !== undefined && { default_enhancement_model }),
    })
    return NextResponse.json(settings)
  } catch (error) {
    console.error('Error updating settings:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to update settings' },
      { status: 500 }
    )
  }
}
