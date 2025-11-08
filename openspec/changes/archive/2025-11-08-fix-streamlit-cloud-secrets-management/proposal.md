## Why

The application crashes on Streamlit Cloud because it directly accesses `st.secrets["ELEVENLABS_API_KEY"]` without handling cases where secrets may not be configured via the Streamlit Cloud dashboard. Additionally, the codebase has inconsistent patterns for API key retrieval—some functions use session state with fallback to secrets (safe), while others directly access secrets (unsafe for cloud deployment).

For a prototype, session-based API key storage is sufficient and appropriate. It allows per-user API keys without requiring a full authentication layer, which is ideal for the current stage of development.

## What Changes

- **Add centralized API key retrieval utility** - Create `get_elevenlabs_api_key()` helper function matching the pattern used for OpenRouter keys
- **Update `app.py`** - Replace direct `st.secrets` access with safe session-state-with-fallback pattern
- **Update `pages/Bulk_Generation.py`** - Replace direct `st.secrets` access with safe pattern
- **Document session storage approach** - Clarify that session-based storage is appropriate for prototype stage
- **Ensure graceful degradation** - App should provide clear guidance when API keys are missing instead of crashing

## Impact

- **Affected specs**: API key management (new capability), TTS generation (modified), bulk generation (modified)
- **Affected code**: 
  - `app.py` (main page initialization)
  - `pages/Bulk_Generation.py` (bulk generation initialization)
  - `utils/` (new helper function)
  - `scripts/Elevenlabs_functions.py` (may need helper function addition)
- **Breaking changes**: None - this is a bug fix that maintains backward compatibility

