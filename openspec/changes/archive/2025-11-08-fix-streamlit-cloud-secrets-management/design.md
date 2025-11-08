## Context

The application currently crashes on Streamlit Cloud because it assumes `st.secrets` is always available. However, Streamlit Cloud requires secrets to be configured via the dashboard, and the app needs to gracefully handle cases where:
1. Secrets are not configured (common during initial deployment)
2. Users want to enter their own API keys per session (multi-user scenario)
3. Development vs production environments differ

The codebase already has a partial solution: `pages/API_Management.py` and `scripts/openrouter_functions.py` use session state with fallback to secrets. We need to extend this pattern consistently across the codebase.

## Goals / Non-Goals

### Goals
- Fix Streamlit Cloud deployment crashes
- Standardize API key retrieval pattern across codebase
- Support session-based API keys for prototype/multi-user scenarios
- Maintain backward compatibility with local development (secrets.toml)

### Non-Goals
- Full authentication layer (not needed for prototype)
- Persistent API key storage (session-only is sufficient)
- User account management
- API key encryption at rest (session state is already handled by Streamlit)

## Decisions

### Decision: Session State First, Secrets Fallback
**Rationale**: 
- Supports multi-user cloud deployment without auth layer
- Allows users to provide their own API keys
- Maintains compatibility with local development via secrets.toml
- Matches existing pattern used for OpenRouter keys

**Implementation**:
```python
def get_elevenlabs_api_key() -> Optional[str]:
    """Get ElevenLabs API key from session state or secrets."""
    return st.session_state.get("ELEVENLABS_API_KEY") or st.secrets.get("ELEVENLABS_API_KEY")
```

### Decision: Graceful Degradation Instead of Hard Failure
**Rationale**:
- Better user experience - users can navigate to API Management page
- Allows partial functionality (e.g., viewing UI) even without keys
- Matches Streamlit best practices for optional configuration

**Implementation**:
- Check for API key at initialization
- Show informative error/warning directing to API Management page
- Use `st.stop()` only when key is required for immediate operation

### Decision: Centralized Helper Function
**Rationale**:
- Consistent pattern across codebase
- Single source of truth for API key retrieval logic
- Easier to test and maintain
- Matches existing `get_openrouter_api_key()` pattern

**Location**: `utils/api_keys.py` (new file) or extend existing utility module

## Risks / Trade-offs

### Risk: Users May Not Realize Keys Are Session-Only
**Mitigation**: Clear messaging in API Management page and error messages explaining session-only storage

### Risk: Performance Impact of Checking Both Sources
**Trade-off**: Negligible - dictionary lookups are O(1) and happen once per page load

### Risk: Session State May Not Persist Across Page Navigations
**Mitigation**: Streamlit session state persists across pages in the same session. Document this behavior clearly.

## Migration Plan

1. **Phase 1**: Add helper function (non-breaking)
2. **Phase 2**: Update `app.py` to use helper (fixes immediate crash)
3. **Phase 3**: Update `pages/Bulk_Generation.py` (fixes bulk generation)
4. **Phase 4**: Add tests and documentation
5. **Rollback**: If issues arise, can revert to direct secrets access (local dev still works)

## Open Questions

- Should we add a helper for OpenRouter keys to `utils/api_keys.py` for consistency, or keep it in `scripts/openrouter_functions.py`?
  - **Decision**: Move to `utils/api_keys.py` for consistency and centralized management

- Should we validate API keys at initialization or lazily when first used?
  - **Decision**: Validate at initialization for better UX (fail fast with clear error)

