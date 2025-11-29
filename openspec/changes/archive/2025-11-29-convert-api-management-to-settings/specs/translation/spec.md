## MODIFIED Requirements

### Requirement: OpenRouter API Integration
The system SHALL integrate with OpenRouter API for translation and language processing services.

#### Scenario: API authentication and configuration
- **WHEN** translation services are accessed
- **THEN** system authenticates with OpenRouter using session-stored API key
- **AND** handles authentication errors with clear user feedback

#### Scenario: Model selection and configuration
- **WHEN** user configures translation settings
- **THEN** system fetches available OpenRouter models from OpenRouter API
- **AND** displays available models for selection with fuzzy search capability
- **AND** allows user to search and filter models by partial name matching
- **AND** provides option to filter models to show only free (zero cost) models
- **AND** uses default translation model from Settings page if no page-specific model is selected
- **AND** falls back to "minimax/minimax-m2:free" if no default is configured
- **AND** page-specific model selection overrides default from Settings
- **AND** provides model-specific configuration options where available
- **AND** caches model list to minimize API calls

#### Scenario: Default model usage
- **WHEN** user attempts translation without selecting a page-specific model
- **THEN** system uses default translation model from Settings (`st.session_state.default_translation_model`)
- **AND** displays indicator showing that default model is being used
- **AND** if no default is configured, displays warning and prevents translation until model is selected

#### Scenario: Fuzzy model search
- **WHEN** user enters partial model name in search field
- **THEN** system filters available models using fuzzy matching algorithm
- **AND** displays matching models sorted by relevance
- **AND** highlights matching portions of model names when possible
- **AND** allows selection from filtered results

#### Scenario: Model fetching and caching
- **WHEN** user accesses translation interface
- **THEN** system fetches available models from OpenRouter API using `@st.cache_data(ttl=3600)` decorator
- **AND** caches model list with appropriate TTL (minimum 1 hour) following Streamlit caching best practices
- **AND** handles API failures gracefully with fallback to default model
- **AND** provides manual refresh option using `st.cache_data.clear()` to update model list
- **AND** cached function returns model data structure for UI consumption

#### Scenario: API response handling
- **WHEN** OpenRouter API returns translation results
- **THEN** system processes response and extracts translated content
- **AND** handles partial responses and error conditions gracefully

