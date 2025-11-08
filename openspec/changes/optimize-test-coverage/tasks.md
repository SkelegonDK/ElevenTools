## 1. Planning and Guardrails

- [x] 1.1 Confirm current pytest collection count and identify redundant tests (>1 scenario overlap).
- [x] 1.2 Define core scenario catalog for API, utilities, and UI pages (map to review-test-suite findings).
- [x] 1.3 Add `core_suite` pytest marker scaffolding and helper to count tests.

## 2. ElevenLabs API Coverage

- [x] 2.1 Consolidate existing ElevenLabs success-path tests via parameterization.
- [x] 2.2 Add error-path scenarios: auth failure, rate limiting, malformed response, filesystem errors.
- [x] 2.3 Remove or fold redundant tests to maintain marker count.

## 3. Streamlit Page Coverage

- [x] 3.1 Add AppTest coverage for `app.py` happy-path interactions.
- [x] 3.2 Add AppTest scenario for Translation page covering submission + error state.
- [x] 3.3 Add AppTest scenario for API Management page including secret validation.
- [x] 3.4 Add AppTest scenario for Voice Design core workflow.

## 4. Utility/Error Handling Coverage

- [x] 4.1 Add parameterized tests for error handling classes/functions (`ElevenToolsError`, `APIError`, `ProgressManager`).
- [x] 4.2 Cover `validate_api_key` and related validation utilities.
- [x] 4.3 Update fixtures/shared helpers to support combined assertions.

## 5. Documentation and Enforcement

- [x] 5.1 Update testing standards (README/testing section + TEST_PATTERNS_GUIDE) with core suite guidance.
- [x] 5.2 Document scenario catalog and maintenance rules in `docs/testing-core-suite.md`.
- [x] 5.3 Add CI script/check ensuring `core_suite` tests < 100 and total coverage threshold met.

## 6. Validation

- [x] 6.1 Run `uv run pytest -m core_suite` and ensure test count < 100.
- [x] 6.2 Run full `uv run pytest` to verify overall success.
- [x] 6.3 Run `uv run coverage run -m pytest` (or existing coverage tool) to capture coverage baseline and document results.

