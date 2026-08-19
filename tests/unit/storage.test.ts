import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { applyExtension, createAudioStore, type AudioStore } from '@/lib/storage'

let root: string
let store: AudioStore

beforeEach(() => {
  root = mkdtempSync(join(tmpdir(), 'eleventools-storage-'))
  store = createAudioStore(root)
})

afterEach(() => {
  rmSync(root, { recursive: true, force: true })
})

const bytes = (s: string) => Buffer.from(s)

describe('applyExtension', () => {
  it('leaves a name that already carries the extension', () => {
    expect(applyExtension('line.mp3', 'mp3')).toBe('line.mp3')
  })

  it('replaces a different extension', () => {
    expect(applyExtension('line.wav', 'pcm')).toBe('line.pcm')
  })

  it('appends when there is no extension', () => {
    expect(applyExtension('line', 'mp3')).toBe('line.mp3')
  })

  it('does not eat a version suffix it cannot mistake for an extension', () => {
    // `.12345678` is too long to be an extension, so the whole name is kept.
    expect(applyExtension('greeting_v1.12345678', 'mp3')).toBe('greeting_v1.12345678.mp3')
  })

  it('is case-insensitive about the existing extension', () => {
    expect(applyExtension('LINE.MP3', 'mp3')).toBe('LINE.MP3')
  })
})

describe('put', () => {
  it('writes the bytes and returns a servable url', () => {
    const stored = store.put('batch-1', 'hello', 'mp3', bytes('AUDIO'))
    expect(stored.filename).toBe('hello.mp3')
    expect(stored.url).toBe('/api/audio/batch-1/hello.mp3')
    expect(readFileSync(join(root, 'batch-1', 'hello.mp3')).toString()).toBe('AUDIO')
  })

  it('applies the output format extension to a mismatched name', () => {
    const stored = store.put('batch-1', 'hello.mp3', 'pcm', bytes('X'))
    expect(stored.filename).toBe('hello.pcm')
  })

  it('resolves collisions instead of overwriting', () => {
    const first = store.put('batch-1', 'line', 'mp3', bytes('ONE'))
    const second = store.put('batch-1', 'line', 'mp3', bytes('TWO'))
    const third = store.put('batch-1', 'line', 'mp3', bytes('THREE'))

    expect([first.filename, second.filename, third.filename]).toEqual([
      'line.mp3',
      'line-2.mp3',
      'line-3.mp3',
    ])
    expect(readFileSync(join(root, 'batch-1', 'line.mp3')).toString()).toBe('ONE')
    expect(readFileSync(join(root, 'batch-1', 'line-2.mp3')).toString()).toBe('TWO')
  })

  it('neutralises traversal in the filename', () => {
    const stored = store.put('batch-1', '../../etc/passwd', 'mp3', bytes('X'))
    expect(stored.filename).toBe('passwd.mp3')
    expect(existsSync(join(root, 'batch-1', 'passwd.mp3'))).toBe(true)
  })

  it('neutralises traversal in the batch id', () => {
    const stored = store.put('../escape', 'x', 'mp3', bytes('X'))
    expect(stored.url).toBe('/api/audio/escape/x.mp3')
  })

  it('rejects a batch id that reduces to nothing', () => {
    expect(() => store.put('..', 'x', 'mp3', bytes('X'))).toThrow(/Invalid path segment/)
  })

  it('url-encodes segments', () => {
    const stored = store.put('batch 1', 'a b', 'mp3', bytes('X'))
    // Spaces are collapsed by the safe character class before encoding.
    expect(stored.url).toBe('/api/audio/batch_1/a_b.mp3')
  })
})

describe('newBatchId', () => {
  it('prefixes and stays unique across calls', () => {
    const a = store.newBatchId('batch')
    const b = store.newBatchId('batch')
    expect(a.startsWith('batch-')).toBe(true)
    expect(a).not.toBe(b)
  })

  it('produces an id that survives its own sanitising', () => {
    const id = store.newBatchId('dialogue')
    const stored = store.put(id, 'x', 'mp3', bytes('X'))
    expect(stored.url).toBe(`/api/audio/${id}/x.mp3`)
  })
})

describe('remove', () => {
  it('deletes the file', () => {
    const stored = store.put('batch-1', 'gone', 'mp3', bytes('X'))
    store.remove(stored.url)
    expect(existsSync(join(root, 'batch-1', 'gone.mp3'))).toBe(false)
  })

  it('removes the batch directory once it is empty', () => {
    const stored = store.put('batch-1', 'only', 'mp3', bytes('X'))
    store.remove(stored.url)
    expect(existsSync(join(root, 'batch-1'))).toBe(false)
  })

  it('keeps a batch directory that still holds files', () => {
    const first = store.put('batch-1', 'a', 'mp3', bytes('X'))
    store.put('batch-1', 'b', 'mp3', bytes('Y'))
    store.remove(first.url)
    expect(existsSync(join(root, 'batch-1'))).toBe(true)
    expect(existsSync(join(root, 'batch-1', 'b.mp3'))).toBe(true)
  })

  it('ignores a path that is not one of ours', () => {
    expect(() => store.remove('/etc/passwd')).not.toThrow()
    expect(existsSync('/etc/passwd')).toBe(true)
  })

  it('is a no-op for a file that is already gone', () => {
    expect(() => store.remove('/api/audio/batch-1/missing.mp3')).not.toThrow()
  })
})

describe('resolveForRead', () => {
  it('resolves a path inside the root', () => {
    store.put('batch-1', 'ok', 'mp3', bytes('X'))
    expect(store.resolveForRead(['batch-1', 'ok.mp3'])).toBe(join(store.root, 'batch-1', 'ok.mp3'))
  })

  it('rejects traversal segments', () => {
    expect(store.resolveForRead(['..', 'etc', 'passwd'])).toBeNull()
    expect(store.resolveForRead(['batch-1', '../../escape'])).toBeNull()
  })

  it('rejects embedded separators', () => {
    expect(store.resolveForRead(['batch-1/nested'])).toBeNull()
    expect(store.resolveForRead(['batch-1\\nested'])).toBeNull()
  })

  it('rejects an empty path', () => {
    expect(store.resolveForRead([])).toBeNull()
  })
})

describe('createAudioStore', () => {
  it('does not create the root until something is written', () => {
    const unused = join(root, 'not-yet')
    createAudioStore(unused)
    expect(existsSync(unused)).toBe(false)
  })
})
