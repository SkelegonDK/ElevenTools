import { NextResponse } from 'next/server'
import { deleteGeneration, getGeneration, getGenerations } from '@/lib/db'
import { deleteAudioFromPath } from '@/lib/storage'

export async function GET() {
  try {
    const generations = getGenerations().map((g) => ({
      id: g.id,
      text: g.text,
      voice_id: g.voice_id,
      model_id: g.model_id,
      blob_url: g.audio_path,
      filename: g.filename,
      created_at: new Date(g.created_at).toISOString(),
      batch_id: g.batch_id,
    }))
    return NextResponse.json({ generations })
  } catch (error) {
    console.error('Error fetching history:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch history' },
      { status: 500 }
    )
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const generationId = searchParams.get('id')

    if (!generationId) {
      return NextResponse.json({ error: 'Generation ID required' }, { status: 400 })
    }

    const existing = getGeneration(generationId)
    if (existing) {
      deleteAudioFromPath(existing.audio_path)
    }
    deleteGeneration(generationId)

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Error deleting generation:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to delete generation' },
      { status: 500 }
    )
  }
}
