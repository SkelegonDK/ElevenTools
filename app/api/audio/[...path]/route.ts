import { NextResponse } from 'next/server'
import { createReadStream, statSync } from 'node:fs'
import { getAudioStore } from '@/lib/storage'

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: segments } = await params

  // The store owns path safety for reads as well as writes, so this route and
  // `put` cannot drift into two different notions of "inside the audio root".
  const filePath = getAudioStore().resolveForRead((segments ?? []).map(decodeURIComponent))
  if (!filePath) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  let stat
  try {
    stat = statSync(filePath)
  } catch {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  if (!stat.isFile()) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  const stream = createReadStream(filePath) as unknown as ReadableStream
  return new Response(stream, {
    headers: {
      'Content-Type': 'audio/mpeg',
      'Content-Length': stat.size.toString(),
      'Cache-Control': 'private, max-age=3600',
    },
  })
}
