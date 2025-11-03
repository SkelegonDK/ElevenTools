## 1. Core API Key Management

- [x] 1.1 Create `get_elevenlabs_api_key()` helper function in `utils/api_keys.py` (or similar utility module)
  - Function should check `st.session_state` first, then fallback to `st.secrets.get()`
  - Return `Optional[str]` to handle missing keys gracefully
  - Add docstring explaining the session-state-first approach

- [x] 1.2 Update `app.py` to use `get_elevenlabs_api_key()` instead of direct `st.secrets` access
  - Replace line 43: `ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]`
  - Handle `None` case with user-friendly error message directing to API Management page
  - Ensure validation still occurs but doesn't crash the app

- [x] 1.3 Update `pages/Bulk_Generation.py` to use `get_elevenlabs_api_key()` 
  - Replace line 24: `st.session_state["ELEVENLABS_API_KEY"] = st.secrets["ELEVENLABS_API_KEY"]`
  - Use helper function instead
  - Handle missing key gracefully

## 2. Error Handling & User Experience

- [x] 2.1 Add informative error messages when API keys are missing
  - Direct users to API Management page
  - Explain that keys can be entered via session (no permanent storage)
  - Link to Streamlit Cloud secrets documentation for production deployment

- [x] 2.2 Ensure API key validation provides helpful feedback
  - Update error messages to distinguish between missing keys and invalid keys
  - Provide actionable next steps in error messages

## 3. Documentation

- [x] 3.1 Document session-based API key approach in README or architecture docs
  - Explain why session storage is appropriate for prototype
  - Clarify that this approach supports multi-user cloud deployment without auth layer
  - Note limitations and when full auth layer might be needed

- [x] 3.2 Update API Management page documentation to reflect the fallback pattern
  - Ensure help text accurately describes the session → secrets fallback behavior

## 4. Testing

- [x] 4.1 Add tests for `get_elevenlabs_api_key()` helper function
  - Test session state priority
  - Test secrets fallback
  - Test missing key handling

- [x] 4.2 Add tests for app initialization with missing secrets
  - Verify app doesn't crash
  - Verify appropriate error messages are shown
  - Verify users can still navigate to API Management page

- [x] 4.3 Update existing tests if needed
  - Ensure all tests use the new helper function pattern
  - Mock both session state and secrets appropriately

