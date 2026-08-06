# ElevenTools — Architecture Overhaul Plan

**Date:** 2026-08-06
**Branch:** `eleventools-v2`
**Source:** architecture review, 7 candidates (01–07)
**Status:** Complete — all 8 phases executed and verified 2026-08-06

**Verification results:** `tsc --noEmit` clean · 106 unit tests pass (was 18) · `next build` succeeds, all 18 routes prerendered · Playwright smoke test green · all 11 anti-pattern greps clean · every dashboard page renders with no console errors.

Vocabulary is the `/codebase-design` glossary: **module**, **interface**, **implementation**, **depth**, **seam**, **adapter**, **leverage**, **locality**.

---

## Phase 0 — Discovery (complete)

### Sources consulted

| File | Read | What it established |
|---|---|---|
| `lib/elevenlabs/api.ts` (223 L) | full | SDK adapter surface; `GenerateAudioParams` (13 fields), `GenerateDialogueParams` (8), `generateAudio`/`generateDialogue` return `{audio, requestId, outputFormat}`; `getVoices`/`getModels` are `unstable_cache`-wrapped; `requireApiKey()` exists |
| `lib/db.ts` (165 L) | full | Module-scope `new Database(DB_PATH)` + DDL + pragma-probe migrations + 9 `prepare()` calls. Exports 6 functions, 3 types. No SQL escapes. |
| `lib/storage.ts` (42 L) | full | Module-scope `mkdirSync(AUDIO_ROOT)`. `safeSegment` private. `deleteAudioFromPath` calls `rmSync(dir, {recursive:false})` — always throws on a directory. |
| `app/api/bulk/generate/route.ts` (155 L) | full | Whole batch loop inline in `POST`; `deriveFilename` module-private; ring buffer; per-row error capture |
| `app/api/elevenlabs/dialogue/route.ts` (138 L) | full | Twin structure; `sanitiseFilename` module-private; `MAX_UNIQUE_VOICES=10`, `MAX_TOTAL_CHARS=2000` |
| `lib/elevenlabs/types.ts` (57 L) | full | Client-safe type module. `OutputFormat` 12-member union, `DEFAULT_OUTPUT_FORMAT`, `extensionForOutputFormat` |
| `lib/utils/model-capabilities.ts` (110 L) | full | 8 predicates + `STABILITY_PRESETS` + `getModelCapabilities`. Consumed only by pages. |
| `lib/utils/csv.ts` (44 L) | full | `parseCSV`, `detectVariables`, `replaceVariables` — the live copies |
| `lib/utils/text-processing.ts` (58 L) | full | **Zero importers** (verified by grep over `app lib components tests`) |
| `app/api/{history,audio/[...path],settings/defaults}/route.ts` | full | history owns row→wire mapping + delete ordering; audio route re-implements traversal safety with `resolve`+prefix |
| `tests/unit/elevenlabs-api.test.ts` (207 L) | full | The mock pattern to copy: `vi.mock('@elevenlabs/elevenlabs-js')` with a hand-rolled class, `await import('@/lib/…')` inside each `it` |
| `vitest.config.ts`, `package.json` | full | `environment: 'node'`, `include: ['tests/unit/**/*.test.ts']`, `globals: true`, `server-only` aliased to a stub. `better-sqlite3 ^12.10.0`. |
| `docs/superpowers/specs/2026-05-28-…-design.md` | full | Approved perf spec. Phase 2 (server cache) is the current uncommitted diff. Phase 3 (RSC + TanStack Query) not started. |

### Allowed APIs — verified, not assumed

**better-sqlite3 (`^12.10.0`)** — as used in the existing `lib/db.ts`:
- `new Database(path)` — `':memory:'` is a valid path
- `db.pragma('journal_mode = WAL')`, `db.pragma('table_info(x)')` → `Array<{name:string}>`
- `db.exec(sql)`, `db.prepare<Params, Row>(sql)` → `.all()` / `.get()` / `.run(namedParams)`

**ElevenLabs SDK (`@elevenlabs/elevenlabs-js ^2.49.1`)** — confirmed in `lib/elevenlabs/api.ts`:
- `client.textToSpeech.convert(voiceId, body).withRawResponse()` → `{ data: ReadableStream, rawResponse: { headers } }`
- `client.textToDialogue.convert(body).withRawResponse()` — same shape
- `client.models.list()`, `client.voices.search()`, `client.voices.get(id)`
- Body fields are **camelCase**: `modelId`, `outputFormat`, `voiceSettings.similarityBoost`, `useSpeakerBoost`, `previousRequestIds`, `applyTextNormalization`, `languageCode`
- Dialogue wraps stability as `settings: { stability }` — **not** a top-level field

**Next.js 15** — confirmed in the working tree:
- `unstable_cache(fn, keyParts, { revalidate, tags })` from `next/cache`
- `revalidateTag(tag)` from `next/cache`
- Route `params` is a **Promise** in Next 15: `{ params }: { params: Promise<{...}> }`

**node:fs** — `rmSync(path, {force:true})` for files; **`rmdirSync`** for removing an empty directory. `rmSync(dir, {recursive:false})` throws `ERR_FS_EISDIR` unconditionally — do not use it for directories.

### Anti-patterns to avoid

- ❌ Do not invent SDK fields. Only the camelCase names listed above exist.
- ❌ Do not add `snake_case` to any SDK call body.
- ❌ Do not import `server-only` into a module a client component will import (`lib/generation/request.ts` must stay SDK-free and `server-only`-free, same rule that `lib/elevenlabs/types.ts` already follows).
- ❌ Do not use `rmSync` to remove a directory.
- ❌ Do not change any exported function name in `lib/db.ts` — every call site depends on the current interface.
- ❌ Do not start the perf-spec Phase 3 work (RSC-ification, TanStack Query). Out of scope here.

---

## Phase 1 — Delete the dead ends (Candidate 07)

**Implement**
1. Delete `lib/utils/text-processing.ts`.
2. `app/(dashboard)/dashboard/translate/page.tsx` — delete the inline re-implementations of `filterFreeModels` / `isModelFree`; import from `@/lib/openrouter/api`.
3. `components/model-selector.tsx` — delete its local `isModelFree`; import the same.
4. Wire `default_translation_model`: translate page seeds its model from `/api/settings/defaults`.
5. `app/api/history/route.ts` — surface `kind`, `seed`, `output_format`, `request_id` instead of dropping them.
6. Settings page — correct the `default_enhancement_model` help text (no enhancement feature exists) and stop blocking save on it.

**Verify** — `rg "text-processing"` returns nothing; `rg "isModelFree" | wc -l` ≤ 1; `pnpm test` green; `npx tsc --noEmit` clean.

**Guard** — do not drop the `default_enhancement_model` column (needs a real migration; no benefit).

---

## Phase 2 — Store factories (Candidate 04)

**Implement**
1. `lib/db.ts` → `createDatabase(path)` returning a store object; module-level lazy default preserves every current export **verbatim**.
2. `lib/storage.ts` → `createAudioStore(root)`; no `mkdirSync` at import; lazy default preserves `AUDIO_ROOT`, `saveAudio`, `deleteAudioFromPath`.
3. Fix `deleteAudioFromPath` — use `rmdirSync` for the empty-batch cleanup.
4. New `tests/unit/db.test.ts` and `tests/unit/storage.test.ts` using `:memory:` and `mkdtempSync`.

**Copy from** — the migration block at `lib/db.ts:38-51` moves verbatim into the factory. The test mock idiom comes from `tests/unit/elevenlabs-api.test.ts:64-70`.

**Verify** — new tests green; `rg "^const db = new Database"` returns nothing; every existing import of `@/lib/db` and `@/lib/storage` still typechecks unchanged.

---

## Phase 3 — Generation request module (Candidate 02)

**Implement** `lib/generation/request.ts` — client-safe, no SDK, no `server-only`:
- `DEFAULT_VOICE_SETTINGS`, `VOICE_SETTING_RANGES`, `SEED_MAX`, `OUTPUT_FORMAT_OPTIONS`, `DIALOGUE_LIMITS`
- `parseBatchRequest(unknown): ParseResult<BatchRequest>`
- `parseDialogueRequest(unknown): ParseResult<DialogueRequest>`
- Clamps ranges, validates the `OutputFormat` union and `TextNormalization` set, bounds the seed, and drops parameters the chosen model does not support (via `getModelCapabilities`).

**Verify** — `tests/unit/generation-request.test.ts` covers clamping, union rejection, seed bounds, capability gating, defaults. Both pages import `DEFAULT_VOICE_SETTINGS` and `OUTPUT_FORMAT_OPTIONS` instead of declaring their own.

**Guard** — the module returns values; it must not throw for invalid input, and must not import anything server-side.

---

## Phase 4 — Audio store owns naming (Candidate 03)

**Implement**
1. Move `deriveFilename` (from `app/api/bulk/generate/route.ts:141`) into `lib/storage.ts` as part of the store's implementation.
2. Add `newBatchId(prefix)` and collision resolution (`name.mp3` → `name-2.mp3`) to `put`.
3. Delete `sanitiseFilename` from the dialogue route.
4. `app/api/audio/[...path]/route.ts` uses a store method for path resolution instead of importing `AUDIO_ROOT` raw.

**Verify** — `tests/unit/storage.test.ts` covers traversal (`../../etc/passwd`), extension swap (`greeting_v1.2` → `greeting_v1.mp3`), collisions, and read-path resolution. `rg "sanitiseFilename"` returns nothing.

---

## Phase 5 — Batch run module (Candidate 01)

**Implement** `lib/generation/batch.ts` — pure, ports injected:
```ts
export interface GenerationPorts {
  generate(p: GenerateAudioParams): Promise<{ audio: ArrayBuffer; requestId: string | null }>
  save(batchId: string, filename: string, bytes: ArrayBuffer): string
  persist(row: InsertGenerationInput): void
  newId(): string
}
export function runBatch(req: BatchRequest, ports: GenerationPorts): Promise<BatchResult>
export function runDialogue(req: DialogueRequest, ports: DialoguePorts): Promise<DialogueResult>
```
Both generate routes shrink to: parse → run → respond.

**Verify** — `tests/unit/generation-batch.test.ts` with in-memory ports asserts prosody sequencing (`previousText`/`nextText`), the request-id ring buffer including the stale-id-after-failure case, per-row error accumulation, and the `{success, failed, results, errors}` contract. No `Request`/`Response` and no real filesystem in the test.

---

## Phase 6 — Cache policy owner (Candidate 05)

**Implement** — declare each catalogue resource's freshness once in `lib/elevenlabs/api.ts` and derive both the `unstable_cache` options and the `Cache-Control` header from it. Collapse `voices/route.ts` and `models/route.ts` onto a shared handler.

**Guard** — this refactors the **uncommitted** perf-spec Phase 2 diff; preserve its behaviour (same TTLs, same headers), do not revert it.

---

## Phase 7 — Client dedup + error surfacing (Candidate 06, scoped)

**Implement**
1. Extract the duplicated `Panel` into `components/ui/panel.tsx`.
2. Both pages import `OUTPUT_FORMAT_OPTIONS` and seed parsing from `lib/generation/request.ts`.
3. Bulk page gains an error state and renders `data.errors` — partial batch failures stop being invisible.

**Out of scope, deliberately** — TanStack Query and the RSC island rework. Those are the approved perf spec's Phase 3; building a second fetching interface here would be thrown away.

---

## Phase 8 — Verification

1. `npx tsc --noEmit`
2. `pnpm test` — all unit suites
3. `pnpm build`
4. `pnpm test:e2e`
5. Anti-pattern grep: `text-processing`, `sanitiseFilename`, `deriveFilename` outside `lib/storage`, `new Database(` at module scope, `rmSync(dir`, `isModelFree` duplicates, `similarity_boost` inside any SDK call body.
