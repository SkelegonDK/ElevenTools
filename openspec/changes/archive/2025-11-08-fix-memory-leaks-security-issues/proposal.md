## Why

The codebase has several memory leak vulnerabilities and security issues that could impact application stability and user safety:

**Memory Leaks:**
- Unbounded session state accumulation in `generated_audio` list grows indefinitely without cleanup
- Cache directory grows unbounded as expired files are only removed on access, not proactively
- Large data structures (models, voices) persist in session state without size limits or cleanup mechanisms

**Security Issues:**
- Path traversal vulnerability where user-controlled CSV filenames are used directly in directory paths
- XSS vulnerability where user input is unescaped before being displayed
- File path construction uses filesystem entries directly without validation
- Missing input validation for file sizes, DataFrame sizes, and column names
- CSS files rendered with `unsafe_allow_html=True` without validation

These issues pose risks for:
- Application crashes due to memory exhaustion
- Unauthorized file system access
- Cross-site scripting attacks
- Denial of service through resource exhaustion

## What Changes

- **Add session state size limits** - Implement maximum size limits for `generated_audio` list and other accumulating session state
- **Implement cache cleanup** - Add background cleanup for expired cache files
- **Sanitize file paths** - Validate and sanitize all user-controlled file paths to prevent traversal
- **Add input validation** - Validate CSV file sizes, DataFrame sizes, and column names before processing
- **Escape user content** - Properly escape all user-controlled content before rendering
- **Validate file paths** - Add validation for filesystem entries used in path construction
- **Add resource limits** - Implement configurable limits for file uploads and data processing

## Impact

- **Affected specs**: Memory management (new capability), Security (new capability), File management (modified), TTS generation (modified), Bulk generation (modified)
- **Affected code**:
  - `app.py` - Session state management, input validation
  - `pages/Bulk_Generation.py` - Path sanitization, file size validation
  - `pages/File_Explorer.py` - Path validation
  - `scripts/Elevenlabs_functions.py` - Path sanitization, input validation
  - `scripts/openrouter_functions.py` - Content escaping
  - `utils/caching.py` - Cache cleanup mechanism
- **Breaking changes**: None - these are security and stability fixes that maintain backward compatibility

