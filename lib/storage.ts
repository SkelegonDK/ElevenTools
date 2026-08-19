import { existsSync, mkdirSync, rmdirSync, rmSync, writeFileSync } from 'node:fs'
import { basename, join, resolve, sep } from 'node:path'

const URL_PREFIX = '/api/audio/'

/**
 * Reduce one path segment to something that cannot escape the audio root:
 * strip any directory component, collapse everything outside the safe
 * character class, and reject the segments that mean "somewhere else".
 */
function safeSegment(segment: string): string {
  const cleaned = basename(segment).replace(/[^a-zA-Z0-9._-]/g, '_')
  if (!cleaned || cleaned === '.' || cleaned === '..') {
    throw new Error(`Invalid path segment: ${segment}`)
  }
  return cleaned
}

/**
 * Apply the output format's extension to a caller-supplied name.
 *
 * A name already ending in the right extension is left alone. Any other
 * trailing dotted extension is replaced, so picking `pcm_24000` cannot leave a
 * PCM payload sitting in a file called `.mp3`.
 */
export function applyExtension(name: string, ext: string): string {
  if (name.toLowerCase().endsWith(`.${ext}`)) return name
  return `${name.replace(/\.[a-z0-9]{1,5}$/i, '')}.${ext}`
}

export interface StoredAudio {
  /** Final on-disk filename, after sanitising, extension policy and collisions. */
  filename: string
  /** URL the app serves it from. */
  url: string
}

/**
 * The audio store owns everything about where a generation's bytes live: batch
 * identity, filename policy, collision handling, reads and deletes. Nothing
 * outside this module constructs a path under the audio root.
 */
export interface AudioStore {
  readonly root: string
  newBatchId(prefix: string): string
  put(batchId: string, name: string, ext: string, bytes: ArrayBuffer | Buffer): StoredAudio
  remove(audioPath: string): void
  /** Absolute path for a URL's segments, or null if it would escape the root. */
  resolveForRead(segments: string[]): string | null
}

export function createAudioStore(root: string): AudioStore {
  const ROOT = resolve(root)

  function ensureRoot(): void {
    mkdirSync(ROOT, { recursive: true })
  }

  /**
   * First free name in the batch: `line.mp3`, then `line-2.mp3`, `line-3.mp3`…
   * Without this, two CSV rows resolving to the same name silently overwrite
   * each other on disk while both get their own history row.
   */
  function uniqueIn(dir: string, filename: string, ext: string): string {
    if (!existsSync(join(dir, filename))) return filename
    const stem = filename.slice(0, filename.length - (ext.length + 1))
    for (let n = 2; ; n++) {
      const candidate = `${stem}-${n}.${ext}`
      if (!existsSync(join(dir, candidate))) return candidate
    }
  }

  return {
    root: ROOT,

    newBatchId(prefix: string): string {
      return `${safeSegment(prefix)}-${Date.now().toString(36)}${Math.floor(Math.random() * 1296)
        .toString(36)
        .padStart(2, '0')}`
    },

    put(batchId, name, ext, bytes): StoredAudio {
      ensureRoot()
      const safeBatch = safeSegment(batchId)
      const dir = join(ROOT, safeBatch)
      mkdirSync(dir, { recursive: true })

      const safeFile = uniqueIn(dir, safeSegment(applyExtension(name, ext)), ext)
      const buffer = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes)
      writeFileSync(join(dir, safeFile), buffer)

      return {
        filename: safeFile,
        url: `${URL_PREFIX}${encodeURIComponent(safeBatch)}/${encodeURIComponent(safeFile)}`,
      }
    },

    remove(audioPath: string): void {
      if (!audioPath.startsWith(URL_PREFIX)) return
      const segments = audioPath.slice(URL_PREFIX.length).split('/').map(decodeURIComponent)
      if (segments.length === 0) return

      const safe = segments.map(safeSegment)
      rmSync(join(ROOT, ...safe), { force: true })

      if (safe.length > 1) {
        try {
          // rmdirSync, not rmSync: rmSync on a directory throws unless
          // `recursive` is set, and recursive would delete a non-empty batch.
          rmdirSync(join(ROOT, ...safe.slice(0, -1)))
        } catch {
          // Batch still holds other files — leave the directory in place.
        }
      }
    },

    resolveForRead(segments: string[]): string | null {
      if (!segments || segments.length === 0) return null
      if (segments.some((s) => s.includes('..') || s.includes('/') || s.includes('\\'))) {
        return null
      }
      const filePath = resolve(join(ROOT, ...segments))
      if (filePath !== ROOT && !filePath.startsWith(ROOT + sep)) return null
      return filePath
    },
  }
}

// ── Default instance ────────────────────────────────────────────────────────
// Lazy, so importing this module neither reads env nor creates directories.

let defaultStore: AudioStore | null = null

export function getAudioStore(): AudioStore {
  if (!defaultStore) {
    defaultStore = createAudioStore(
      process.env.ELEVENTOOLS_AUDIO_PATH || join(process.cwd(), 'data', 'audio')
    )
  }
  return defaultStore
}

export const saveAudio = (
  batchId: string,
  name: string,
  ext: string,
  bytes: ArrayBuffer | Buffer
): StoredAudio => getAudioStore().put(batchId, name, ext, bytes)

export const deleteAudioFromPath = (audioPath: string): void => getAudioStore().remove(audioPath)
