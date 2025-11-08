## ADDED Requirements

### Requirement: Centralized API Key Retrieval
The system SHALL provide centralized helper functions for retrieving API keys that check session state first, then fall back to Streamlit secrets.

#### Scenario: ElevenLabs API key from session state
- **WHEN** a user has entered their ElevenLabs API key via the API Management page
- **THEN** the `get_elevenlabs_api_key()` function returns the key from session state

#### Scenario: ElevenLabs API key from secrets fallback
- **WHEN** no API key exists in session state but a key exists in `st.secrets`
- **THEN** the `get_elevenlabs_api_key()` function returns the key from secrets

#### Scenario: Missing API key handling
- **WHEN** no API key exists in either session state or secrets
- **THEN** the `get_elevenlabs_api_key()` function returns `None`

### Requirement: Graceful API Key Initialization
The application SHALL handle missing API keys gracefully without crashing, providing clear guidance to users.

#### Scenario: Missing API key on app initialization
- **WHEN** the main page (`app.py`) loads and no ElevenLabs API key is available
- **THEN** the app displays an informative error message directing users to the API Management page
- **AND** the app does not crash or raise unhandled exceptions

#### Scenario: Missing API key on bulk generation page
- **WHEN** the bulk generation page loads and no ElevenLabs API key is available
- **THEN** the page displays an informative error message
- **AND** users can navigate to the API Management page to enter their key

### Requirement: Session-Based API Key Storage for Prototype
The system SHALL support session-based API key storage as the primary method for multi-user cloud deployment without requiring a full authentication layer.

#### Scenario: User enters API key in session
- **WHEN** a user enters their API key via the API Management page
- **THEN** the key is stored in `st.session_state` for the current session only
- **AND** the key is not persisted to disk or shared between users
- **AND** the key is available for all pages during the session

#### Scenario: Session-based keys work across pages
- **WHEN** a user enters an API key on the API Management page
- **THEN** the key is immediately available on the main page and bulk generation page
- **AND** the key persists across page navigations within the same browser session

## MODIFIED Requirements

### Requirement: API Key Initialization in Main Page
The main page (`app.py`) SHALL retrieve the ElevenLabs API key using the centralized helper function with session state fallback to secrets, instead of directly accessing `st.secrets`.

#### Scenario: Safe API key retrieval on main page
- **WHEN** the main page initializes
- **THEN** it uses `get_elevenlabs_api_key()` to retrieve the API key
- **AND** if no key is available, it shows a user-friendly error message instead of crashing

### Requirement: API Key Initialization in Bulk Generation Page
The bulk generation page (`pages/Bulk_Generation.py`) SHALL retrieve the ElevenLabs API key using the centralized helper function, matching the pattern used on the main page.

#### Scenario: Safe API key retrieval on bulk generation page
- **WHEN** the bulk generation page initializes
- **THEN** it uses `get_elevenlabs_api_key()` to retrieve the API key
- **AND** if no key is available, it handles the missing key gracefully

