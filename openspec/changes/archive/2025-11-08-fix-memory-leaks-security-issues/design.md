## Context

The application has memory leak vulnerabilities and security issues that need to be addressed to ensure stability and security. Memory leaks can cause application crashes in long-running sessions, while security vulnerabilities could allow unauthorized access or attacks.

## Goals / Non-Goals

### Goals
- Prevent memory leaks through bounded session state and cache cleanup
- Prevent path traversal attacks through proper path sanitization
- Prevent XSS attacks through content escaping
- Add comprehensive input validation to prevent DoS and injection attacks
- Maintain backward compatibility with existing functionality

### Non-Goals
- Complete rewrite of session state management (incremental improvements only)
- Advanced security features like rate limiting or authentication (out of scope)
- Database-backed session management (keep session-based approach)
- Real-time memory monitoring dashboard (logging sufficient)

## Decisions

### Decision: Bounded Session State Lists
**What**: Implement maximum size limits for accumulating session state lists (e.g., `generated_audio` max 100 entries)
**Why**: Prevents unbounded memory growth while preserving recent history
**Alternatives considered**:
- Unlimited with manual cleanup (rejected - users won't remember to clean)
- Time-based expiration (rejected - adds complexity, less predictable)
- Database storage (rejected - overkill for prototype, adds dependencies)

**Implementation**:
```python
MAX_GENERATED_AUDIO_HISTORY = 100
if len(st.session_state["generated_audio"]) >= MAX_GENERATED_AUDIO_HISTORY:
    st.session_state["generated_audio"] = st.session_state["generated_audio"][-MAX_GENERATED_AUDIO_HISTORY:]
```

### Decision: Proactive Cache Cleanup
**What**: Add cleanup mechanism that removes expired cache files on access or periodically
**Why**: Prevents cache directory from growing unbounded
**Alternatives considered**:
- Cleanup only on access (rejected - doesn't prevent growth)
- Separate cleanup thread (rejected - adds complexity, Streamlit doesn't support threads well)
- Cleanup on app startup (accepted - simple, effective)

**Implementation**:
```python
def cleanup_expired_cache():
    """Remove expired cache files."""
    for file in os.listdir(cache_dir):
        if file.endswith(".json"):
            cache_path = os.path.join(cache_dir, file)
            # Check expiration and remove if expired
```

### Decision: Path Sanitization Utility
**What**: Create centralized `sanitize_path_component()` function for all path construction
**Why**: Ensures consistent security across all file operations
**Alternatives considered**:
- Inline sanitization (rejected - code duplication, inconsistent)
- Whitelist approach (accepted - more secure than blacklist)

**Implementation**:
```python
def sanitize_path_component(component: str, max_length: int = 100) -> str:
    """Sanitize a path component to prevent traversal."""
    # Remove path separators and dangerous characters
    sanitized = re.sub(r'[\\/:*?"<>|]', '_', component)
    # Limit length
    sanitized = sanitized[:max_length]
    # Ensure not empty or just dots
    if not sanitized or sanitized in ('.', '..'):
        sanitized = 'default'
    return sanitized
```

### Decision: Input Validation Limits
**What**: Set reasonable limits for file sizes (10MB), DataFrame rows (1000), and text length (10K chars)
**Why**: Prevents DoS attacks and memory exhaustion
**Alternatives considered**:
- No limits (rejected - security risk)
- Configurable limits (accepted - allows adjustment per deployment)
- Very strict limits (rejected - breaks legitimate use cases)

**Implementation**:
```python
MAX_CSV_SIZE = 10 * 1024 * 1024  # 10MB
MAX_DF_ROWS = 1000
MAX_TEXT_LENGTH = 10000
```

### Decision: Content Escaping for User Input
**What**: Escape all user-controlled content before rendering in Streamlit
**Why**: Prevents XSS attacks
**Alternatives considered**:
- Trust all content (rejected - security risk)
- Markdown sanitization library (considered - may add dependency)
- HTML escaping (accepted - simple, effective for Streamlit)

**Implementation**:
```python
import html
# Escape before display
safe_content = html.escape(user_input)
st.markdown(safe_content)
```

## Risks / Trade-offs

### Risk: Breaking Existing Functionality
**Mitigation**: Add limits that are generous enough for normal use, make limits configurable

### Risk: Performance Impact of Validation
**Mitigation**: Validation is lightweight, cache cleanup runs infrequently

### Risk: False Positives in Path Sanitization
**Mitigation**: Use whitelist approach, test thoroughly with edge cases

## Migration Plan

1. **Phase 1**: Add memory limits (non-breaking, just prevents growth)
2. **Phase 2**: Add path sanitization (non-breaking, improves security)
3. **Phase 3**: Add input validation (may reject some previously accepted inputs - document breaking changes)
4. **Phase 4**: Add content escaping (non-breaking, improves security)

## Open Questions

- Should cache cleanup run on every app startup or only periodically?
- What should happen when input validation fails - error message or automatic truncation?
- Should we add a "clear history" button for users to manually clean session state?

