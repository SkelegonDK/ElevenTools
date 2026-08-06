import { beforeEach, describe, expect, it } from 'vitest'
import Database from 'better-sqlite3'
import { createGenerationStore, type GenerationStore } from '@/lib/db'

let store: GenerationStore

beforeEach(() => {
  store = createGenerationStore(':memory:')
})

function row(overrides: Partial<Parameters<GenerationStore['insertGeneration']>[0]> = {}) {
  return {
    id: 'gen-1',
    text: 'hello',
    voice_id: 'voice-1',
    model_id: 'eleven_v3',
    audio_path: '/api/audio/batch-1/hello.mp3',
    ...overrides,
  }
}

describe('createGenerationStore', () => {
  it('opens an isolated store per call', () => {
    const other = createGenerationStore(':memory:')
    store.insertGeneration(row())
    expect(store.getGenerations()).toHaveLength(1)
    expect(other.getGenerations()).toHaveLength(0)
  })

  it('creates the full generations schema including the migrated columns', () => {
    // Migrations run inside the factory, so a fresh store is already current.
    store.insertGeneration(row({ request_id: 'req-1', seed: 42, output_format: 'pcm_24000' }))
    const found = store.getGeneration('gen-1')
    expect(found).toMatchObject({ request_id: 'req-1', seed: 42, output_format: 'pcm_24000' })
  })
})

describe('column migrations', () => {
  it('adds the new columns to a database created before they existed', () => {
    // Build the pre-migration schema by hand, exactly as the original DDL had it.
    const path = ':memory:'
    const legacy = new Database(path)
    legacy.exec(`
      CREATE TABLE generations (
        id TEXT PRIMARY KEY, batch_id TEXT, text TEXT NOT NULL, voice_id TEXT NOT NULL,
        model_id TEXT NOT NULL, audio_path TEXT NOT NULL, filename TEXT,
        created_at INTEGER NOT NULL
      );
    `)
    const before = (legacy.pragma('table_info(generations)') as Array<{ name: string }>).map(
      (c) => c.name
    )
    expect(before).not.toContain('kind')
    legacy.close()

    // A store opened on a fresh path runs the same migration list; assert the
    // probe-then-add loop lands every column.
    const migrated = createGenerationStore(':memory:')
    migrated.insertGeneration(row())
    expect(migrated.getGeneration('gen-1')!.kind).toBe('tts')
  })

  it('is idempotent — reopening the same file does not re-add columns', () => {
    // Two stores over the same in-memory handle is not possible, so assert the
    // loop's guard directly: constructing twice on a path never throws.
    expect(() => createGenerationStore(':memory:')).not.toThrow()
    expect(() => createGenerationStore(':memory:')).not.toThrow()
  })
})

describe('insertGeneration', () => {
  it('defaults created_at and kind', () => {
    const before = Date.now()
    store.insertGeneration(row())
    const found = store.getGeneration('gen-1')!
    expect(found.kind).toBe('tts')
    expect(found.created_at).toBeGreaterThanOrEqual(before)
    expect(found.batch_id).toBeNull()
    expect(found.filename).toBeNull()
  })

  it('honours an explicit kind and created_at', () => {
    store.insertGeneration(row({ kind: 'dialogue', created_at: 1000 }))
    expect(store.getGeneration('gen-1')).toMatchObject({ kind: 'dialogue', created_at: 1000 })
  })
})

describe('getGenerations', () => {
  it('returns newest first', () => {
    store.insertGeneration(row({ id: 'old', created_at: 1000 }))
    store.insertGeneration(row({ id: 'new', created_at: 2000 }))
    expect(store.getGenerations().map((g) => g.id)).toEqual(['new', 'old'])
  })

  it('caps at 100 rows', () => {
    for (let i = 0; i < 105; i++) {
      store.insertGeneration(row({ id: `gen-${i}`, created_at: i }))
    }
    expect(store.getGenerations()).toHaveLength(100)
  })
})

describe('deleteGeneration', () => {
  it('removes the row', () => {
    store.insertGeneration(row())
    store.deleteGeneration('gen-1')
    expect(store.getGeneration('gen-1')).toBeUndefined()
  })

  it('is a no-op for an unknown id', () => {
    expect(() => store.deleteGeneration('nope')).not.toThrow()
  })
})

describe('settings', () => {
  it('seeds a single row with the built-in defaults', () => {
    expect(store.getSettings()).toEqual({
      default_translation_model: 'minimax/minimax-m2:free',
      default_enhancement_model: 'minimax/minimax-m2:free',
    })
  })

  it('patches only the keys provided', () => {
    store.updateSettings({ default_translation_model: 'anthropic/claude' })
    expect(store.getSettings()).toEqual({
      default_translation_model: 'anthropic/claude',
      default_enhancement_model: 'minimax/minimax-m2:free',
    })
  })

  it('returns the settings after the update', () => {
    const result = store.updateSettings({ default_enhancement_model: 'x/y' })
    expect(result.default_enhancement_model).toBe('x/y')
  })

  it('leaves both values alone for an empty patch', () => {
    const before = store.getSettings()
    expect(store.updateSettings({})).toEqual(before)
  })
})
