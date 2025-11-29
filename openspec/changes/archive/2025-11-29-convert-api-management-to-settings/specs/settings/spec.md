## MODIFIED Requirements

### Requirement: Settings Page
The system SHALL provide a unified Settings page for configuring application preferences including API keys and default model selections.

#### Scenario: Settings page access
- **WHEN** user navigates to Settings page
- **THEN** system displays API Key Management section with current key status
- **AND** displays Default Translation Model selection section
- **AND** displays Default Script Enhancement Model selection section
- **AND** all sections are clearly separated and labeled

#### Scenario: API key management in settings
- **WHEN** user accesses Settings page
- **THEN** system displays current API key status for ElevenLabs and OpenRouter
- **AND** allows users to update API keys stored in session state
- **AND** shows source of each API key (Session, Secrets, or Not set)
- **AND** provides clear instructions for API key configuration

### Requirement: Default Translation Model Configuration
The system SHALL allow users to configure a default translation model in Settings that will be used when no page-specific model is selected.

#### Scenario: Default translation model selection
- **WHEN** user accesses Settings page
- **THEN** system displays model selection UI matching Translation page (fuzzy search, free filter, model dropdown)
- **AND** shows current default translation model
- **AND** allows user to search and select a new default translation model
- **AND** stores selected model in `st.session_state.default_translation_model`
- **AND** defaults to "minimax/minimax-m2:free" if no model is configured

#### Scenario: Default translation model persistence
- **WHEN** user selects a default translation model in Settings
- **THEN** system stores selection in session state
- **AND** selection persists across page navigation within the same session
- **AND** selected model is used for all translations when no page-specific model is selected

#### Scenario: Default translation model validation
- **WHEN** user attempts to use translation without configuring default model
- **THEN** system displays warning message guiding user to Settings page
- **AND** prevents translation operation until model is configured

### Requirement: Default Script Enhancement Model Configuration
The system SHALL allow users to configure a default script enhancement model in Settings that will be used when no page-specific model is selected.

#### Scenario: Default enhancement model selection
- **WHEN** user accesses Settings page
- **THEN** system displays model selection UI matching Translation page (fuzzy search, free filter, model dropdown)
- **AND** shows current default enhancement model
- **AND** allows user to search and select a new default enhancement model
- **AND** stores selected model in `st.session_state.default_enhancement_model`
- **AND** defaults to "minimax/minimax-m2:free" if no model is configured

#### Scenario: Default enhancement model persistence
- **WHEN** user selects a default enhancement model in Settings
- **THEN** system stores selection in session state
- **AND** selection persists across page navigation within the same session
- **AND** selected model is used for all script enhancements when no page-specific model is selected

#### Scenario: Default enhancement model validation
- **WHEN** user attempts to use script enhancement without configuring default model
- **THEN** system displays warning message guiding user to Settings page
- **AND** prevents enhancement operation until model is configured

### Requirement: Settings Access from Pages
The system SHALL provide easy access to Settings page from Translation and main app pages.

#### Scenario: Settings access from Translation page
- **WHEN** user views Translation page
- **THEN** system displays gear icon (⚙️) near page title or model selection section
- **AND** clicking gear icon navigates to Settings page
- **AND** gear icon has tooltip indicating it leads to settings for default model configuration

#### Scenario: Settings access from main app page
- **WHEN** user views main app page
- **THEN** system displays gear icon (⚙️) near script enhancement section
- **AND** clicking gear icon navigates to Settings page
- **AND** gear icon has tooltip indicating it leads to settings for default model configuration

