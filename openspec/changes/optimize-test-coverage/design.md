## Context

- Test review shows 192 pytest cases, many targeting similar permutations.
- ElevenLabs API functions lack negative-path coverage; UI pages (app, translation, API management, voice design) lack any tests.
- Maintaining 190+ bespoke tests is unsustainable; goal is to keep suite < 100 cases.

## Goals

- Cover every P0/P1 gap identified in review-test-suite documentation.
- Merge redundant assertions via parameterization or helper assertions.
- Keep aggregate pytest collection count `< 100`.
- Maintain or improve runtime (target < 90s locally).

## Non-Goals

- Achieve 100% branch coverage.
- Rewrite production code.
- Add end-to-end browser automation (Streamlit testing only).

## Decisions

- **Scenario Catalog:** Group API tests by scenario class (success, auth failure, rate limit, filesystem error). One parameterized test per class with table-driven inputs.
- **UI Coverage:** Use Streamlit AppTest to cover each high-priority page with single holistic regression test capturing main interactions, rather than multiple granular tests.
- **Utilities:** Combine exception class tests into a single parameterized test verifying inheritance, message, and handling for each subclass.
- **Guardrail:** Add pytest custom marker `@pytest.mark.core_suite` for all curated tests. Validation step counts only marked tests to ensure `< 100`.

## Alternatives Considered

- **Full rewrite using playwright:** rejected (too heavy for Streamlit, exceeds test count goal).
- **Retain existing fine-grained tests and add more:** rejected due to maintenance burden and explicit instruction to keep suite moderate.

## Risks / Trade-offs

- Consolidated tests may hide granular failure context; mitigated by descriptive parameter ids.
- Parameterization increases fixture complexity; mitigated with helper factory functions in `conftest.py`.
- Core suite filter relies on discipline; mitigated by adding CI check to enforce count.

## Migration Plan

1. Inventory existing tests, tag keepers with `@pytest.mark.core_suite`.
2. Fold overlapping tests into parameterized variants.
3. Add new coverage for missing scenarios.
4. Delete superseded granular tests.
5. Update documentation and run enforcement script counting core tests.

## Open Questions

- What minimum coverage percentage should CI enforce alongside test count?
- Should non-core exploratory tests live in a separate optional directory?

