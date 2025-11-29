# Translation & Localization Specification

## Purpose
The Translation & Localization capability provides multi-language script translation and phonetic conversion using OpenRouter API integration, supporting the text-to-speech workflow.
## Requirements
### Requirement: Multi-Language Translation
The system SHALL provide text translation between multiple languages using OpenRouter API integration.

#### Scenario: Language selection and translation
- **WHEN** user selects source and target languages for translation
- **THEN** system translates input text using OpenRouter API
- **AND** displays translated text with language detection confidence

#### Scenario: Automatic language detection
- **WHEN** user inputs text without specifying source language
- **THEN** system automatically detects source language using OpenRouter
- **AND** provides confidence score and allows manual override if needed

#### Scenario: Translation quality feedback
- **WHEN** translation is completed
- **THEN** system displays both original and translated text side-by-side
- **AND** provides options for manual editing and refinement

### Requirement: Phonetic Conversion Support
The system SHALL provide phonetic conversion capabilities to improve text-to-speech pronunciation accuracy.

#### Scenario: Phonetic conversion request
- **WHEN** user requests phonetic conversion for text
- **THEN** system processes text through OpenRouter for phonetic representation
- **AND** returns phonetically optimized text for TTS generation

#### Scenario: Language-specific phonetics
- **WHEN** phonetic conversion is applied to specific languages
- **THEN** system uses language-appropriate phonetic rules and conventions
- **AND** optimizes output for target TTS model capabilities

#### Scenario: Phonetic preview and editing
- **WHEN** phonetic conversion is generated
- **THEN** system displays original and phonetic versions
- **AND** allows manual editing of phonetic representation

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

### Requirement: Translation Workflow Integration
The system SHALL integrate translation capabilities with the broader text-to-speech workflow.

#### Scenario: Translation to TTS pipeline
- **WHEN** user completes text translation
- **THEN** system provides direct option to generate TTS from translated text
- **AND** maintains translation context and language settings for TTS generation

#### Scenario: Bulk translation support
- **WHEN** user wants to translate multiple texts for bulk TTS generation
- **THEN** system supports batch translation processing
- **AND** integrates with bulk generation CSV workflow

#### Scenario: Translation history and reuse
- **WHEN** user performs translations
- **THEN** system maintains translation history within session
- **AND** allows reusing previous translations for efficiency

### Requirement: Language Support and Validation
The system SHALL provide comprehensive language support with validation and error handling.

#### Scenario: Supported languages display
- **WHEN** user accesses translation interface
- **THEN** system displays list of supported source and target languages
- **AND** provides language codes and full language names

#### Scenario: Language pair validation
- **WHEN** user selects source and target languages
- **THEN** system validates that translation between selected languages is supported
- **AND** provides alternative suggestions for unsupported language pairs

#### Scenario: Content validation for translation
- **WHEN** user inputs text for translation
- **THEN** system validates text length, format, and character encoding
- **AND** provides feedback for content that may not translate well

### Requirement: Translation Cache and Performance
The system SHALL implement caching and performance optimization for translation operations.

#### Scenario: Translation result caching
- **WHEN** identical translation requests are made
- **THEN** system returns cached results instead of making new API calls
- **AND** cache respects session boundaries and user privacy

#### Scenario: Translation request optimization
- **WHEN** multiple translation requests are queued
- **THEN** system optimizes API calls through batching where possible
- **AND** manages rate limits and concurrent request constraints

#### Scenario: Performance feedback and progress
- **WHEN** translation processing takes significant time
- **THEN** system provides progress indicators and estimated completion time
- **AND** allows cancellation of long-running translation requests

### Requirement: Error Handling and Fallbacks
The system SHALL provide robust error handling and fallback mechanisms for translation operations.

#### Scenario: API error management
- **WHEN** OpenRouter API returns errors or is unavailable
- **THEN** system provides clear error messages with suggested actions
- **AND** implements retry logic with exponential backoff for transient errors

#### Scenario: Translation quality issues
- **WHEN** translation results are low quality or incomplete
- **THEN** system provides quality indicators and warnings
- **AND** offers options for retranslation with different parameters

#### Scenario: Network and connectivity issues
- **WHEN** network connectivity issues affect translation requests
- **THEN** system handles timeouts and connection errors gracefully
- **AND** provides offline indicators and retry mechanisms

### Requirement: Translation Output Formatting
The system SHALL provide proper formatting and presentation of translation results.

#### Scenario: Side-by-side translation display
- **WHEN** translation is completed
- **THEN** system displays original and translated text in clear, comparable format
- **AND** maintains text formatting and structure where possible

#### Scenario: Translation metadata display
- **WHEN** translation results are shown
- **THEN** system displays metadata including detected source language, confidence scores, and model used
- **AND** provides timestamp and allows saving translation pairs

#### Scenario: Export and sharing capabilities
- **WHEN** user wants to export translation results
- **THEN** system provides options for copying, downloading, or sharing translations
- **AND** maintains proper formatting and attribution information

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

