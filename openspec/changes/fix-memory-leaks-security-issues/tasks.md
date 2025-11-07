## 1. Memory Management

- [x] 1.1 Add size limit to `generated_audio` session state list (max 100 entries, keep most recent)
- [x] 1.2 Implement automatic cleanup of old entries when limit is reached
- [x] 1.3 Add cache cleanup mechanism to `utils/caching.py` for expired files
- [x] 1.4 Add periodic cache cleanup task or cleanup on cache access
- [x] 1.5 Add size limits to models/voices session state (with refresh mechanism)
- [ ] 1.6 Add memory monitoring utilities for production debugging

## 2. Security - Path Traversal Prevention

- [x] 2.1 Create path sanitization utility function in `utils/`
- [x] 2.2 Sanitize CSV filename in `pages/Bulk_Generation.py` before using in path
- [x] 2.3 Validate output directory paths in `bulk_generate_audio()` function
- [x] 2.4 Add path validation in `pages/File_Explorer.py` for filesystem entries
- [x] 2.5 Add tests for path traversal prevention

## 3. Security - Input Validation

- [x] 3.1 Add CSV file size validation (max 10MB recommended)
- [x] 3.2 Add DataFrame row limit validation (max 1000 rows)
- [x] 3.3 Validate CSV column names (alphanumeric + underscore only)
- [x] 3.4 Add text input length limits for script enhancement
- [x] 3.5 Add validation for filename template length and characters

## 4. Security - Content Escaping

- [x] 4.1 Escape user content in `scripts/openrouter_functions.py` before display
- [x] 4.2 Review all `st.markdown()` calls for user-controlled content
- [x] 4.3 Ensure CSS file reading is safe (validate file location)
- [x] 4.4 Add HTML escaping utility function
- [x] 4.5 Add tests for XSS prevention

## 5. Testing & Documentation

- [x] 5.1 Write tests for memory limit enforcement
- [x] 5.2 Write tests for path traversal prevention
- [x] 5.3 Write tests for input validation
- [x] 5.4 Write tests for content escaping
- [ ] 5.5 Update security documentation with new requirements
- [ ] 5.6 Add security best practices to developer guidelines

