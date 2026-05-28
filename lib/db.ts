import Database from 'better-sqlite3'
import { mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'

const DEFAULT_TRANSLATION_MODEL = 'minimax/minimax-m2:free'
const DEFAULT_ENHANCEMENT_MODEL = 'minimax/minimax-m2:free'

const DB_PATH = process.env.ELEVENTOOLS_DB_PATH || join(process.cwd(), 'data', 'eleventools.db')

mkdirSync(dirname(DB_PATH), { recursive: true })

const db = new Database(DB_PATH)
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

const selectGenerations = db.prepare<[], Generation>(
  `SELECT id, batch_id, text, voice_id, model_id, audio_path, filename, created_at,
          request_id, seed, output_format, kind
   FROM generations
   ORDER BY created_at DESC
   LIMIT 100`
)

const selectGenerationById = db.prepare<[string], Generation>(
  `SELECT id, batch_id, text, voice_id, model_id, audio_path, filename, created_at,
          request_id, seed, output_format, kind
   FROM generations
   WHERE id = ?`
)

const insertGenerationStmt = db.prepare(
  `INSERT INTO generations (
     id, batch_id, text, voice_id, model_id, audio_path, filename, created_at,
     request_id, seed, output_format, kind
   ) VALUES (
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

export function getGenerations(): Generation[] {
  return selectGenerations.all()
}

export function getGeneration(id: string): Generation | undefined {
  return selectGenerationById.get(id)
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

export function insertGeneration(row: InsertGenerationInput): void {
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
}

export function deleteGeneration(id: string): void {
  deleteGenerationStmt.run(id)
}

export function getSettings(): Settings {
  return selectSettings.get()!
}

export function updateSettings(patch: Partial<Settings>): Settings {
  updateSettingsStmt.run({
    default_translation_model: patch.default_translation_model ?? null,
    default_enhancement_model: patch.default_enhancement_model ?? null,
  })
  return getSettings()
}
