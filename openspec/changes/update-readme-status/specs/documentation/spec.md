## ADDED Requirements

### Requirement: Comprehensive Project Documentation
The project SHALL maintain accurate and up-to-date documentation that reflects the current state of the application, including all implemented features, testing capabilities, and configuration requirements.

#### Scenario: README accuracy for current features
- **WHEN** users or contributors read the README.md file
- **THEN** the documentation accurately describes all implemented features including OpenRouter model selection with fuzzy search
- **AND** version information matches the project version in pyproject.toml
- **AND** testing documentation includes Playwright UI tests and comprehensive test coverage details

#### Scenario: Configuration documentation completeness
- **WHEN** users set up the application for the first time
- **THEN** README.md provides clear instructions for all required API keys (ElevenLabs and OpenRouter)
- **AND** configuration examples include all necessary secrets.toml entries

#### Scenario: Testing documentation accuracy
- **WHEN** developers want to run tests
- **THEN** README.md accurately lists all test files and directories
- **AND** provides correct commands for running unit tests and Playwright UI tests
- **AND** reflects the actual test organization structure

## MODIFIED Requirements

### Requirement: Project Status Tracking
The project SHALL maintain an accurate TODO list that reflects completed work and current priorities.

#### Scenario: TODO list accuracy
- **WHEN** users or contributors review the TODO list in README.md
- **THEN** completed features are marked as done
- **AND** outdated items are removed or updated
- **AND** the list accurately reflects current project priorities and status
- **AND** references to `docs/todo.md` are removed or updated to indicate OpenSpec is now used for task management

#### Scenario: Documentation references accuracy
- **WHEN** users or contributors look for project documentation
- **THEN** README.md does not reference outdated `docs/` folder structure (todo.md, design.md, architecture.md)
- **AND** documentation clearly indicates that OpenSpec is used for task management and spec-driven development
- **AND** any references to old documentation structure are updated or removed

