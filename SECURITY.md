# Security Documentation

This document outlines the security measures implemented in ElevenTools to protect against common vulnerabilities and ensure safe operation in multi-user environments.

## Security Requirements

### Path Traversal Prevention

**Risk**: User-controlled file paths could be used to access files outside intended directories.

**Protection**:
- All user-provided filenames and path components are sanitized using `utils.security.sanitize_path_component()`
- Path validation ensures resolved paths remain within base directories using `utils.security.validate_path_within_base()`
- CSV filenames are sanitized before use in directory paths
- File Explorer validates all filesystem entries before display

**Implementation**:
- `utils/security.py`: Core sanitization and validation functions
- `pages/Bulk_Generation.py`: CSV filename sanitization
- `pages/File_Explorer.py`: Path validation for filesystem entries
- `scripts/Elevenlabs_functions.py`: Output directory path validation

**Testing**: See `tests/test_utils/test_security.py` for path traversal prevention tests.

### Input Validation

**Risk**: Unvalidated user input could cause resource exhaustion or application crashes.

**Protection**:
- **CSV File Size**: Maximum 10MB per CSV file (`MAX_CSV_SIZE = 10 * 1024 * 1024`)
- **DataFrame Rows**: Maximum 1000 rows per DataFrame (`MAX_DF_ROWS = 1000`)
- **Column Names**: Only alphanumeric characters and underscores allowed
- **Text Input**: Maximum 10,000 characters for script enhancement (`MAX_TEXT_LENGTH = 10000`)
- **Filename Length**: Maximum 100 characters (`MAX_FILENAME_LENGTH = 100`)

**Implementation**:
- `utils/security.py`: Validation functions for all input types
- Validation occurs before processing in all relevant pages and functions

**Testing**: See `tests/test_utils/test_security.py` for input validation tests.

### Cross-Site Scripting (XSS) Prevention

**Risk**: User-controlled content rendered without escaping could execute malicious scripts.

**Protection**:
- All user-controlled content is escaped before display using `utils.security.escape_html_content()`
- HTML escaping applied to all content displayed via `st.markdown()` with user input
- CSS file reading validates file location before loading

**Implementation**:
- `utils/security.py`: `escape_html_content()` function using Python's `html.escape()`
- `scripts/openrouter_functions.py`: Content escaping before display
- All `st.markdown()` calls reviewed for user-controlled content

**Testing**: See `tests/test_utils/test_security.py` for XSS prevention tests.

### Memory Leak Prevention

**Risk**: Unbounded session state accumulation could cause application crashes.

**Protection**:
- **Session State Limits**: `generated_audio` list limited to 100 entries (keeps most recent)
- **Automatic Cleanup**: Old entries automatically removed when limits reached
- **Cache Cleanup**: Expired cache files automatically cleaned up
- **Size Limits**: Models/voices session state have size limits with refresh mechanisms

**Implementation**:
- `app.py`: Session state size limits and automatic cleanup
- `utils/caching.py`: Cache cleanup mechanism
- `utils/memory_monitoring.py`: Memory monitoring utilities for debugging

**Monitoring**: Use `utils.memory_monitoring.log_session_state_memory()` for production debugging.

## API Key Management

### Secure Storage

**Session-Based Storage** (Recommended for Cloud):
- API keys stored only in browser session state
- Never saved to disk or shared between users
- Perfect for multi-user cloud deployments

**Streamlit Secrets** (For Streamlit Cloud):
- Configured via Streamlit Cloud dashboard
- Shared across all users of deployed app
- See [Streamlit Cloud Secrets Documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

**Local secrets.toml** (For Development):
- Stored in `.streamlit/secrets.toml` (never commit to git)
- Used for local development only

### Priority Order

1. Session state (user-entered keys via Settings page)
2. Streamlit secrets (cloud dashboard or local secrets.toml)

## Session-Based File Isolation

### Privacy Protection

- Each user session gets unique directory: `outputs/{session_id}/`
- Files from other users' sessions are not accessible
- Session ID persists across page navigations
- Automatic cleanup of old session directories (default: 24 hours)

**Implementation**: See `utils/session_manager.py` for session management.

## Security Best Practices for Developers

### When Adding New Features

1. **Always validate user input** before processing
   - Use functions from `utils/security.py`
   - Check file sizes, row counts, and text lengths
   - Validate column names and filenames

2. **Sanitize all file paths** before use
   - Use `sanitize_path_component()` for user-provided filenames
   - Use `validate_path_within_base()` for path validation
   - Never use user input directly in file paths

3. **Escape user content** before display
   - Use `escape_html_content()` for all user-controlled content
   - Review all `st.markdown()` calls for user input
   - Never use `unsafe_allow_html=True` with user content

4. **Limit session state accumulation**
   - Set maximum sizes for accumulating lists
   - Implement automatic cleanup when limits reached
   - Monitor memory usage in production

5. **Never hardcode secrets**
   - Use `st.secrets` or session state for API keys
   - Never commit secrets to git
   - Use `.gitignore` for secrets files

### Code Review Checklist

- [ ] All user inputs validated (size, format, length)
- [ ] All file paths sanitized and validated
- [ ] All user content escaped before display
- [ ] Session state lists have size limits
- [ ] No secrets hardcoded in code
- [ ] Error messages don't leak sensitive information
- [ ] File operations validate paths before access

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do not** open a public issue
2. Email security concerns to [your contact information]
3. Include details about the vulnerability and steps to reproduce

## Security Testing

All security measures are tested in `tests/test_utils/test_security.py`:
- Path traversal prevention tests
- Input validation tests
- XSS prevention tests
- Memory limit enforcement tests

Run security tests:
```bash
uv run pytest tests/test_utils/test_security.py -v
```

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Streamlit Security Best Practices](https://docs.streamlit.io/develop/concepts/security)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

