## Why

The current pytest suite contains 192 individual test cases spread across API, utility, and UI modules. While the review-test-suite analysis identified critical coverage gaps, it also revealed extensive redundancy and over-granular assertions that inflate upkeep cost. We need a focused expansion that raises coverage for high-impact flows (app shell, voice design, translation, API error paths) without letting the test count balloon. The goal is a curated test suite with fewer than 100 total tests that still exercises all priority scenarios.

## What Changes

- Consolidate overlapping ElevenLabs API tests into parameterized cases while adding missing error-path coverage.
- Add high-value Streamlit page regression tests (app shell, translation, API management, voice design) using scenario-based fixtures instead of one-test-per-widget.
- Introduce targeted tests for error handling utilities and progress manager with combined assertions.
- Remove or fold redundant tests so the final suite stays under 100 tests while meeting new coverage targets.
- Document the curated scenario catalog and guardrail for future contributors (how to keep the suite lean).

## Impact

- Affected specs: `testing`
- Affected code: `tests/test_api`, `tests/test_streamlit`, `tests/test_utils`, shared fixtures in `tests/conftest.py`
- Operational impact: faster CI runs, clearer regression signal, enforceable ceiling on redundant test additions
- No production runtime changes; scope limited to tests and test documentation

