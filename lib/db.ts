import Database from 'better-sqlite3'
import { mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'

const DEFAULT_TRANSLATION_MODEL = 'minimax/minimax-m2:free'
const DEFAULT_ENHANCEMENT_MODEL = 'minimax/minimax-m2:free'

export interface Generation {
  id: string
  batch_id: string | null
  text: string
  voice_id: string
  model_id: string
  audio_path: string
  filename: string | null
  created_at: number
  request_id: string | null
  seed: number | null
  output_format: string | null
  kind: string
}

export interface Settings {
  default_translation_model: string
  default_enhancement_model: string
}

export interface InsertGenerationInput {
  id: string
  batch_id?: string | null
  text: string
  voice_id: string
  model_id: string
  audio_path: string
  filename?: string | null
  created_at?: number
  request_id?: string | null
  seed?: number | null
  output_format?: string | null
  kind?: 'tts' | 'dialogue'
}

/**
 * Everything a caller can do with the generation store. Callers never see SQL,
 * column lists, or the `better-sqlite3` handle.
 */
export interface GenerationStore {
  getGenerations(): Generation[]
  getGeneration(id: string): Generation | undefined
  insertGeneration(row: InsertGenerationInput): void
  deleteGeneration(id: string): void
  getSettings(): Settings
  updateSettings(patch: Partial<Settings>): Settings
  close(): void
}

/**
 * Open a store at `path`. Pass `':memory:'` for an ephemeral one — that is the
 * adapter the unit tests use, and the reason construction lives in a function
 * rather than at module scope.
 *
 * Schema creation and column migrations run here, so every store instance is
 * fully migrated by the time it is returned.
 */
export function createGenerationStore(path: string): GenerationStore {
  if (path !== ':memory:') {
    mkdirSync(dirname(path), { recursive: true })
  }

  const db = new Database(path)
  db.pragma('journal_mode = WAL')
  db.pragma('foreign_keys = ON')

  db.exec(`
    CREATE TABLE IF NOT EXISTS generations (
      id TEXT PRIMARY KEY,
      batch_id TEXT,
      text TEXT NOT NULL,
      voice_id TEXT NOT NULL,
      model_id TEXT NOT NULL,
      audio_path TEXT NOT NULL,
      filename TEXT,
      created_at INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_generations_created_at ON generations(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_generations_batch_id ON generations(batch_id);

    CREATE TABLE IF NOT EXISTS settings (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      default_translation_model TEXT NOT NULL DEFAULT '${DEFAULT_TRANSLATION_MODEL}',
      default_enhancement_model TEXT NOT NULL DEFAULT '${DEFAULT_ENHANCEMENT_MODEL}'
    );
    INSERT OR IGNORE INTO settings (id) VALUES (1);
  `)

  // Idempotent column additions for the generations table.
  // SQLite has no ADD COLUMN IF NOT EXISTS, so probe pragma first.
  const existingColumns = new Set<string>(
    (db.pragma('table_info(generations)') as Array<{ name: string }>).map((c) => c.name)
  )
  const COLUMN_MIGRATIONS: Array<{ name: string; ddl: string }> = [
    { name: 'request_id', ddl: 'ALTER TABLE generations ADD COLUMN request_id TEXT' },
    { name: 'seed', ddl: 'ALTER TABLE generations ADD COLUMN seed INTEGER' },
    { name: 'output_format', ddl: 'ALTER TABLE generations ADD COLUMN output_format TEXT' },
    { name: 'kind', ddl: "ALTER TABLE generations ADD COLUMN kind TEXT NOT NULL DEFAULT 'tts'" },
  ]
  for (const m of COLUMN_MIGRATIONS) {
    if (!existingColumns.has(m.name)) db.exec(m.ddl)
  }

  const GENERATION_COLUMNS = `id, batch_id, text, voice_id, model_id, audio_path, filename,
     created_at, request_id, seed, output_format, kind`

  const selectGenerations = db.prepare<[], Generation>(
    `SELECT ${GENERATION_COLUMNS} FROM generations ORDER BY created_at DESC LIMIT 100`
  )

  const selectGenerationById = db.prepare<[string], Generation>(
    `SELECT ${GENERATION_COLUMNS} FROM generations WHERE id = ?`
  )

  const insertGenerationStmt = db.prepare(
    `INSERT INTO generations (${GENERATION_COLUMNS}) VALUES (
       @id, @batch_id, @text, @voice_id, @model_id, @audio_path, @filename, @created_at,
       @request_id, @seed, @output_format, @kind
     )`
  )

  const deleteGenerationStmt = db.prepare(`DELETE FROM generations WHERE id = ?`)

  const selectSettings = db.prepare<[], Settings>(
    `SELECT default_translation_model, default_enhancement_model FROM settings WHERE id = 1`
  )

  const updateSettingsStmt = db.prepare(
    `UPDATE settings
     SET default_translation_model = COALESCE(@default_translation_model, default_translation_model),
         default_enhancement_model = COALESCE(@default_enhancement_model, default_enhancement_model)
     WHERE id = 1`
  )

  function readSettings(): Settings {
    return selectSettings.get()!
  }

  return {
    getGenerations: () => selectGenerations.all(),
    getGeneration: (id) => selectGenerationById.get(id),
    insertGeneration(row) {
      insertGenerationStmt.run({
        id: row.id,
        batch_id: row.batch_id ?? null,
        text: row.text,
        voice_id: row.voice_id,
        model_id: row.model_id,
        audio_path: row.audio_path,
        filename: row.filename ?? null,
        created_at: row.created_at ?? Date.now(),
        request_id: row.request_id ?? null,
        seed: row.seed ?? null,
        output_format: row.output_format ?? null,
        kind: row.kind ?? 'tts',
      })
    },
    deleteGeneration: (id) => void deleteGenerationStmt.run(id),
    getSettings: readSettings,
    updateSettings(patch) {
      updateSettingsStmt.run({
        default_translation_model: patch.default_translation_model ?? null,
        default_enhancement_model: patch.default_enhancement_model ?? null,
      })
      return readSettings()
    },
    close: () => db.close(),
  }
}

// ── Default instance ────────────────────────────────────────────────────────
// Created lazily on first use rather than at import, so importing this module
// has no side effects and `ELEVENTOOLS_DB_PATH` is read when it is needed.

let defaultStore: GenerationStore | null = null

export function getStore(): GenerationStore {
  if (!defaultStore) {
    const path =
      process.env.ELEVENTOOLS_DB_PATH || join(process.cwd(), 'data', 'eleventools.db')
    defaultStore = createGenerationStore(path)
  }
  return defaultStore
}

export const getGenerations = (): Generation[] => getStore().getGenerations()
export const getGeneration = (id: string): Generation | undefined => getStore().getGeneration(id)
export const insertGeneration = (row: InsertGenerationInput): void =>
  getStore().insertGeneration(row)
export const deleteGeneration = (id: string): void => getStore().deleteGeneration(id)
export const getSettings = (): Settings => getStore().getSettings()
export const updateSettings = (patch: Partial<Settings>): Settings =>
  getStore().updateSettings(patch)
