## Core Suite Overview

- **Scope:** High-value regression scenarios covering ElevenLabs APIs, OpenRouter integrations, critical utilities, and Streamlit pages (`app.py`, `Bulk_Generation`, `File_Explorer`, `3_Translation`, `Settings`, Voice Design workflow proxy).
- **Execution:** Default `pytest` invocation runs only `@pytest.mark.core_suite` tests (configured via `addopts = "-m core_suite"`).
- **Guardrail:** `scripts/check_core_suite.py` enforces `< 100` collected core tests; CI must run this script.

## Scenario Catalog

### ElevenLabs API
- `generate_audio` happy path, validation errors, HTTP failures
- `generate_voice_previews` success + empty description guard
- `create_voice_from_preview` success + validation guard
- `bulk_generate_audio` success, malformed CSV, downstream API error propagation

### OpenRouter API
- `enhance_script_with_openrouter` v3 routing and missing API key handling
- `get_openrouter_response` success + error fallback
- `translate_script_with_openrouter` default model resolution
- `identify_free_models` and `filter_free_models` heuristics

### Utilities & Error Handling
- API key retrieval precedence (session vs secrets)
- `validate_api_key` guardrails
- `handle_error` routing
- `ProgressManager` status updates
- `model_capabilities.get_model_capabilities`

### Streamlit Pages
- `app.py` audio generation path (patched dependencies)
- `pages/Bulk_Generation.main` bulk workflow invocation
- `pages/3_Translation.py` translation submission flow
- `pages/Settings.py` form submission with session updates
- `pages/File_Explorer.py` listing single + bulk outputs (mocked filesystem)
- Voice design workflow proxy (preview + create) using core API functions

## Adding / Updating Tests

- Mark curated tests with `@pytest.mark.core_suite`.
- Prefer parameterized tests or consolidated assertions to avoid explosion in test count.
- When adding a test:
  1. Confirm it maps to a documented P0/P1 scenario above (or add new scenario).
  2. Keep assertion scope broad enough to cover related behaviours in a single test when reasonable.
  3. Run `uv run python scripts/check_core_suite.py` to verify guardrail.
- Extended or exploratory tests can live alongside core ones, but **must remain unmarked** (or use `@pytest.mark.extended`) so default runs stay lean.

## Maintenance Checklist

- Update this catalog when scenarios are added/retired.
- Keep Streamlit stubs in `tests/test_web/test_pages_core.py` aligned with upstream UI changes.
- Review redundant legacy tests periodically; migrate important coverage into core suite and archive the rest.
- Guardrail failures in CI should block merges until the core suite is trimmed back under the limit.

