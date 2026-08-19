# ElevenTools — Performance & Responsiveness Architecture

**Date:** 2026-05-28
**Branch:** `eleventools-v2`
**Status:** Approved (auto-approved under `/goal` directive)

## Goal

Improve perceived performance and responsiveness across the app via architectural changes, focused on the two pains the user flagged:

1. **Page/navigation feels sluggish** — cold loads, voices/models re-fetched on every mount.
2. **App startup / first paint feels heavy** — large client bundle, dynamic-by-default rendering, unused deps.

Bulk-generation throughput is **explicitly out of scope** for this work.

## Constraints (locked)

- Next.js 15 App Router + React 19 — no framework swap.
- SQLite + local filesystem + no auth — no remote DB, no Redis.
- Existing brutalist/mono UI stays — restructure data flow, do not redesign components.

## Approach: Hybrid (RSC shell + client islands with hydrated data)

The dashboard becomes server-first: shells, headers, sidebar chrome, settings, history, and dashboard home are React Server Components. Interactive subtrees (sliders, file upload, audio player, transmit button, voice/model dropdowns) remain `"use client"` islands, but receive **initial data** from their RSC parent so they paint with content on the first frame instead of triggering a network round-trip.

A tiny client cache layer (TanStack Query) sits inside the client islands so that subsequent interactions (refetch, dropdown re-open, route round-trip) dedupe and reuse server-provided data. The server side wraps `fetchVoices`/`fetchModels` in `unstable_cache` with tags for invalidation.

## What changes — by layer

### 1. Bundle trim (Phase 1 — safest, ship first)

- **Remove `three`** from `package.json` (verified unused: only grep hit is the word "three" in a comment).
- Audit `lucide-react` imports — verify tree-shaking is working; otherwise switch to per-icon imports.
- Add an explicit `next build` size budget script under `scripts/check-bundle-size.mjs` that fails CI if the main client bundle grows past a baseline (captured at end of phase 1).

### 2. Dashboard layout: kill dynamic-render triggers (Phase 1)

`app/(dashboard)/layout.tsx` currently uses `Math.random()` (line 26) for a session ID and `new Date().toISOString()` (line 45) in server render. These force the entire dashboard tree to render dynamically every request and cause hydration mismatches.

- Move both into a small `"use client"` `<SessionBadge />` component that computes them on mount with `useEffect`. The static shell can then be statically rendered.

### 3. Sidebar: split server chrome from client nav (Phase 2)

`components/sidebar.tsx` is fully `"use client"` because `usePathname()` is used to compute `isActive`.

- Refactor into:
  - `Sidebar` (server) — wordmark, section labels, footer stack block, all static chrome.
  - `NavLinks` (client) — only the `<Link>` list with active-state computation.
- Net effect: less client JS per page, identical visual output.

### 4. Server-side data caching (Phase 2)

In `lib/elevenlabs/api.ts`:

- Wrap `fetchVoices` and `fetchModels` in `unstable_cache`:
  - `fetchVoices`: `tags: ['voices']`, `revalidate: 1800` (30 min).
  - `fetchModels`: `tags: ['models']`, `revalidate: 3600` (60 min).
- Provide `revalidateVoices()` / `revalidateModels()` helpers using `revalidateTag` for a future "refresh" button.

In the route handlers (`app/api/elevenlabs/voices/route.ts`, `app/api/elevenlabs/models/route.ts`):

- Add `Cache-Control: private, max-age=600, stale-while-revalidate=1800` so the browser also caches.
- These routes remain (used by client islands for refetch), but their server impl now reads from the `unstable_cache` layer.

### 5. RSC-ify pages and hydrate islands (Phase 3)

- **`/dashboard`** — already RSC, no change.
- **`/dashboard/settings`** — convert page to RSC. Reads settings via `getSettings()` (sync, SQLite). Renders a `<SettingsForm initialSettings={...}>` client island that posts mutations via a server action.
- **`/dashboard/history`** — convert page to RSC. Reads `getGenerations()` server-side, renders `<HistoryList initial={...}>` client island for playback/delete interactions.
- **`/dashboard/bulk`** — page becomes RSC shell. Fetches voices + models server-side (cached) and hands them to a single `<BulkGenerator initialVoices={...} initialModels={...}>` client island that owns all the interactive state (sliders, CSV, transmit, results).
- **`/dashboard/dialogue`** — same pattern as bulk.
- **`/dashboard/translate`** — same pattern; fetches OpenRouter models server-side, hands to a `<TranslateForm initialModels={...}>` island.

Each client island accepts an `initial*` prop and seeds TanStack Query's cache via `initialData` so the first render uses server-provided data, and any later refetch goes through the client cache.

### 6. Client cache (Phase 3)

Add `@tanstack/react-query` (~13KB gz). Wire a `QueryClientProvider` inside `app/(dashboard)/layout.tsx` via a tiny `"use client"` `<Providers>` component.

- `staleTime` matches server cache TTL so refetches don't fire spuriously.
- Used exclusively inside client islands. Server components do not touch it.

### 7. Suspense boundaries (Phase 3)

Wrap each RSC data fetch in `<Suspense fallback={<Skeleton />}>` so the page shell paints immediately while the dropdowns/lists stream in. Skeletons match the brutalist style (existing panel borders with dimmed text).

### 8. Nav prefetch (Phase 3)

`<Link>` already prefetches routes on hover by default in Next 15. Add a `onMouseEnter` handler on sidebar nav items that ALSO warms the relevant `unstable_cache` entries via a fire-and-forget fetch, so the data is hot when the user arrives.

## Out of scope

- Bulk generation concurrency / streaming progress (user explicitly deprioritized).
- Auth, multi-user, multi-device.
- Replacing SQLite or the filesystem store.
- Visual redesign.
- Streaming the audio response itself (single-shot TTS is fine for current use).

## File-level plan

| File | Change | Phase |
|---|---|---|
| `package.json` | Remove `three` and `@types/three` if present | 1 |
| `app/(dashboard)/layout.tsx` | Extract `Math.random()` + `new Date()` to `<SessionBadge />` client island | 1 |
| `components/session-badge.tsx` | NEW — tiny client component for session id + ISO date | 1 |
| `scripts/check-bundle-size.mjs` | NEW — bundle size guard | 1 |
| `components/sidebar.tsx` | Convert to server; extract `<NavLinks />` | 2 |
| `components/nav-links.tsx` | NEW — client component for active-state nav | 2 |
| `lib/elevenlabs/api.ts` | Wrap `fetchVoices`/`fetchModels` in `unstable_cache`; add revalidate helpers | 2 |
| `app/api/elevenlabs/voices/route.ts` | Use cached fetch; add `Cache-Control` | 2 |
| `app/api/elevenlabs/models/route.ts` | Use cached fetch; add `Cache-Control` | 2 |
| `app/api/elevenlabs/voices/[voiceId]/route.ts` | Add `Cache-Control` | 2 |
| `app/(dashboard)/dashboard/settings/page.tsx` | RSC + `<SettingsForm>` island + server action | 3 |
| `app/(dashboard)/dashboard/history/page.tsx` | RSC + `<HistoryList>` island | 3 |
| `app/(dashboard)/dashboard/bulk/page.tsx` | RSC shell + `<BulkGenerator>` island with hydrated data | 3 |
| `app/(dashboard)/dashboard/dialogue/page.tsx` | RSC shell + `<DialogueForm>` island | 3 |
| `app/(dashboard)/dashboard/translate/page.tsx` | RSC shell + `<TranslateForm>` island | 3 |
| `components/providers.tsx` | NEW — TanStack QueryClient provider | 3 |
| `app/(dashboard)/layout.tsx` | Wrap children in `<Providers>` | 3 |

## Success criteria

Measured against `eleventools-v2` baseline (commit `68e92a0`):

1. **First Load JS for `/dashboard/bulk`** (per `next build` output): **reduce by ≥30%**. Primary driver: removing `three` + RSC-ifying the bulk page.
2. **Sidebar repeat-navigation feel**: subjectively instant — moving from `/dashboard/history` to `/dashboard/bulk` should not re-fetch voices or models from ElevenLabs (server cache hit + client cache hit).
3. **No hydration warnings** in the dashboard layout (`Math.random` issue fixed).
4. **Existing Vitest suite remains green** (18 tests). Playwright bulk smoke test remains green.

## Risk and rollback

- **Risk**: TanStack Query hydration mismatch if `initialData` shape drifts from server. **Mitigation**: types are shared from `lib/elevenlabs/types.ts` already.
- **Risk**: `unstable_cache` is unstable API and could break on a Next.js minor bump. **Mitigation**: it's locked behind small helper functions; swap point is one file.
- **Rollback**: each phase is one or more atomic commits on a clean branch — `git revert` undoes any phase independently.

## Sequencing

Phases ship as separate commits, executed in order:

1. **Phase 1 — Bundle trim + dynamic-render fixes** (low risk, immediate first-paint win)
2. **Phase 2 — Server caching + sidebar split** (medium, isolated changes)
3. **Phase 3 — RSC-ify pages + client query layer** (largest diff; gated on phase 1 + 2 being green)

A new implementation plan generated by `writing-plans` will expand each phase into ordered, atomic tasks.
