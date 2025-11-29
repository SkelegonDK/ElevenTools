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
- **AND** defaults to "openrouter/auto" if no model is explicitly selected
- **AND** provides model-specific configuration options where available
- **AND** caches model list to minimize API calls

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

## ADDED Requirements

### Requirement: Model Discovery and Search
The system SHALL provide users with the ability to discover and search OpenRouter models using fuzzy matching for translation operations.

#### Scenario: Model list retrieval
- **WHEN** translation page is loaded
- **THEN** system retrieves list of available models from OpenRouter API endpoint
- **AND** displays model information including name, provider, pricing, and description when available
- **AND** identifies and marks free models (zero cost) for filtering
- **AND** handles API errors with user-friendly messages

#### Scenario: Fuzzy search functionality
- **WHEN** user types in model search field
- **THEN** system performs fuzzy matching against available model names using `on_change` callback
- **AND** returns models ranked by match similarity score
- **AND** supports partial matches and typos
- **AND** updates results in real-time as user types (using Streamlit widget callbacks)
- **AND** respects free model filter when enabled
- **AND** search query is stored in session state for persistence

#### Scenario: Model selection persistence
- **WHEN** user selects a model for translation
- **THEN** system stores selected model in `st.session_state.selected_model`
- **AND** uses widget `key` parameter to associate selection widget with session state
- **AND** optionally uses `on_change` callback to update session state when selection changes
- **AND** persists selection across translation operations within same session
- **AND** uses selected model for all subsequent translations until changed
- **AND** initializes default value from session state if key exists

### Requirement: Model Selection Testing
The system SHALL have comprehensive test coverage for model selection, search, and filtering functionality.

#### Scenario: Unit test coverage for model operations
- **WHEN** model fetching, filtering, and search functions are implemented
- **THEN** unit tests verify correct API response parsing and model identification
- **AND** unit tests verify fuzzy search algorithm accuracy with various queries
- **AND** unit tests verify free model filtering logic with different pricing structures
- **AND** unit tests verify error handling for API failures and edge cases

#### Scenario: Playwright UI test coverage for model selection
- **WHEN** model selection UI is implemented
- **THEN** Playwright tests verify model list is fetched and displayed on page load
- **AND** Playwright tests verify fuzzy search input filters models in real-time
- **AND** Playwright tests verify free model filter toggle works correctly
- **AND** Playwright tests verify model selection persists and is used for translation
- **AND** Playwright tests verify error messages display when API fails

#### Scenario: Free model filtering
- **WHEN** user enables free model filter option
- **THEN** system filters available models to show only models with zero cost
- **AND** stores filter state in `st.session_state.show_free_only` (boolean)
- **AND** uses `st.checkbox` or `st.toggle` widget with `key` parameter for state management
- **AND** applies free filter in combination with fuzzy search when both are active
- **AND** displays clear indication when free filter is active
- **AND** preserves filter state during session using session state
- **AND** updates filtered model list immediately using widget callbacks

