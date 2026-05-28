import { NextResponse } from 'next/server'
import { createReadStream, statSync } from 'node:fs'
import { join, resolve, sep } from 'node:path'
import { AUDIO_ROOT } from '@/lib/storage'

const ROOT = resolve(AUDIO_ROOT)

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: segments } = await params

  if (!segments || segments.length === 0) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  const decoded = segments.map(decodeURIComponent)
  if (decoded.some((s) => s.includes('..') || s.includes('/') || s.includes('\\'))) {
    return NextResponse.json({ error: 'Invalid path' }, { status: 400 })
  }

  const filePath = resolve(join(ROOT, ...decoded))
  if (filePath !== ROOT && !filePath.startsWith(ROOT + sep)) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
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
