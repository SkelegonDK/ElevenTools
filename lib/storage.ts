import { mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { basename, join } from 'node:path'

export const AUDIO_ROOT = process.env.ELEVENTOOLS_AUDIO_PATH || join(process.cwd(), 'data', 'audio')

mkdirSync(AUDIO_ROOT, { recursive: true })

function safeSegment(segment: string): string {
  const cleaned = basename(segment).replace(/[^a-zA-Z0-9._-]/g, '_')
  if (!cleaned || cleaned === '.' || cleaned === '..') {
    throw new Error(`Invalid path segment: ${segment}`)
  }
  return cleaned
}

export function saveAudio(batchId: string, filename: string, bytes: ArrayBuffer | Buffer): string {
  const safeBatch = safeSegment(batchId)
  const safeFile = safeSegment(filename)
  const dir = join(AUDIO_ROOT, safeBatch)
  mkdirSync(dir, { recursive: true })
  const buffer = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes)
  writeFileSync(join(dir, safeFile), buffer)
  return `/api/audio/${encodeURIComponent(safeBatch)}/${encodeURIComponent(safeFile)}`
}

export function deleteAudioFromPath(audioPath: string): void {
  const prefix = '/api/audio/'
  if (!audioPath.startsWith(prefix)) return
  const segments = audioPath.slice(prefix.length).split('/').map(decodeURIComponent)
  if (segments.length === 0) return
  const safe = segments.map(safeSegment)
  const target = join(AUDIO_ROOT, ...safe)
  rmSync(target, { force: true })
  if (safe.length > 1) {
    const dir = join(AUDIO_ROOT, ...safe.slice(0, -1))
    try {
      rmSync(dir, { recursive: false })
    } catch {
      // Directory not empty — leave it
    }
  }
}
