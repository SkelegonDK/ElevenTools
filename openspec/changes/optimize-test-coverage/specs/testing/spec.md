## MODIFIED Requirements

### Requirement: Comprehensive Test Coverage
The test suite SHALL provide coverage for all application capabilities as defined in specifications and SHALL maintain a curated `core_suite` of fewer than 100 parameterized tests that exercise every P0/P1 scenario.

#### Scenario: Spec-aligned test coverage
- **WHEN** reviewing test suite
- **THEN** all spec-defined scenarios have corresponding test cases
- **AND** test coverage gaps are documented with priorities

#### Scenario: Page-level test coverage
- **WHEN** reviewing Streamlit page tests
- **THEN** all pages (app.py, Bulk_Generation, File_Explorer, Translation, API_Management, Voice Design) have test coverage
- **AND** page tests validate UI components, user interactions, and error states

#### Scenario: API function test coverage
- **WHEN** reviewing API function tests
- **THEN** all ElevenLabs and OpenRouter functions have unit tests
- **AND** tests cover success cases, error cases, and edge conditions

#### Scenario: Core suite size guardrail
- **WHEN** counting pytest tests marked `core_suite`
- **THEN** the collected test count is fewer than 100
- **AND** the core suite still includes all P0 and P1 scenarios identified in review-test-suite documentation

### Requirement: Test Documentation and Reporting
The test suite SHALL have documentation and reporting capabilities for coverage and gaps, including maintenance rules for the `core_suite` catalog.

#### Scenario: Test coverage reporting
- **WHEN** reviewing test suite
- **THEN** coverage gaps are documented with priorities
- **AND** missing test scenarios are mapped to spec requirements

#### Scenario: Test execution validation
- **WHEN** running test suite
- **THEN** all tests execute successfully with `uv run pytest`
- **AND** test failures are documented and addressed

#### Scenario: Testing best practices documentation
- **WHEN** reviewing testing patterns
- **THEN** project testing standards and patterns are documented
- **AND** guidelines support consistent test development

#### Scenario: Core suite catalog publication
- **WHEN** onboarding contributors
- **THEN** documentation describes the `core_suite` scenarios, marker usage, and guardrails for keeping the suite below 100 tests
- **AND** CI instructions explain how the guardrail is enforced

## ADDED Requirements

### Requirement: Core Test Suite Governance
The project SHALL enforce the `core_suite` size and coverage guardrails through automation.

#### Scenario: Automated guardrail check
- **WHEN** running CI validation
- **THEN** a script verifies that pytest collection of `core_suite` tests remains under 100
- **AND** the job fails if the limit is exceeded or required scenarios are missing

