## Context

The application currently stores all generated files in a shared `outputs/` directory without session isolation. This creates privacy concerns in multi-user cloud deployments where users can potentially see each other's files. Additionally, there's no download functionality, making files inaccessible after generation in ephemeral cloud environments.

## Goals / Non-Goals

### Goals
- Isolate files by session to prevent cross-user file access
- Provide download functionality for individual and bulk files
- Implement automatic cleanup of old session directories
- Maintain backward compatibility during migration
- Ensure security with proper path validation

### Non-Goals
- Persistent cloud storage integration (S3, etc.) - out of scope
- User authentication system - session-based isolation is sufficient
- File sharing between sessions - each session is isolated
- Database-backed file metadata - use filesystem metadata

## Decisions

### Decision: Session ID-Based Directory Structure
**What**: Store files in `outputs/{session_id}/single/` and `outputs/{session_id}/bulk/` directories
**Why**: 
- Simple filesystem-based isolation
- No database required
- Easy cleanup (delete entire session directory)
- Works with ephemeral filesystems

**Implementation**:
```python
# Generate session ID on first use
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

session_output_dir = os.path.join("outputs", st.session_state["session_id"])
```

### Decision: Streamlit Session State for Session ID
**What**: Use Streamlit's built-in session state to track session ID
**Why**:
- Streamlit automatically manages session state per user
- No additional infrastructure needed
- Session ID persists across page navigations
- Resets on browser session end

**Limitation**: Session ID resets on browser refresh in some cases, but this is acceptable for privacy isolation.

### Decision: Download via st.download_button
**What**: Use Streamlit's `st.download_button` for file downloads
**Why**:
- Built-in Streamlit functionality
- Handles file serving automatically
- Works in cloud deployments
- Simple implementation

**Implementation**:
```python
with open(file_path, "rb") as f:
    st.download_button(
        label="Download",
        data=f.read(),
        file_name=filename,
        mime="audio/mpeg"
    )
```

### Decision: Cleanup on Startup
**What**: Run cleanup of old session directories when app starts
**Why**:
- Prevents disk space issues
- Simple to implement
- Doesn't impact user experience
- Can be extended to periodic cleanup later

**Implementation**:
```python
def cleanup_old_sessions(max_age_hours=24):
    """Remove session directories older than max_age_hours."""
    outputs_dir = os.path.join(os.getcwd(), "outputs")
    if not os.path.exists(outputs_dir):
        return
    
    current_time = time.time()
    for entry in os.listdir(outputs_dir):
        session_dir = os.path.join(outputs_dir, entry)
        if os.path.isdir(session_dir):
            # Check directory age
            dir_age = current_time - os.path.getmtime(session_dir)
            if dir_age > (max_age_hours * 3600):
                shutil.rmtree(session_dir)
```

### Decision: Session Timeout Configuration
**What**: Make session timeout configurable via environment variable or config
**Why**:
- Different deployments may need different retention policies
- Allows adjustment without code changes
- Default of 24 hours balances usability and storage

**Implementation**:
```python
SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
```

## Risks / Trade-offs

### Risk: Session ID Reset on Browser Refresh
**Mitigation**: Acceptable trade-off for privacy. Users can regenerate files if needed.

### Risk: Cleanup Removing Active Sessions
**Mitigation**: Use directory modification time, not creation time. Active sessions update mtime on file operations.

### Risk: Storage Accumulation
**Mitigation**: Aggressive cleanup (24 hours) and configurable timeout. Can add manual cleanup UI later.

### Risk: Path Traversal in Session IDs
**Mitigation**: Validate session IDs are valid UUIDs, sanitize paths.

## Migration Plan

1. **Phase 1**: Add session management without breaking existing structure
2. **Phase 2**: New files go to session directories, old files remain accessible
3. **Phase 3**: Add cleanup to remove old shared directories after migration period
4. **Phase 4**: Update File Explorer to only show session files

## Open Questions

- Should we preserve old `outputs/single/` structure for backward compatibility?
- Should cleanup be more aggressive (e.g., 1 hour) for cloud deployments?
- Should we add a "Clear My Files" button for users?

