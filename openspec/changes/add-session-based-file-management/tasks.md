## 1. Session Management

- [x] 1.1 Create session ID generation utility in `utils/session_manager.py`
- [x] 1.2 Generate unique session ID on app initialization
- [x] 1.3 Store session ID in session state
- [x] 1.4 Create session directory structure: `outputs/{session_id}/single/` and `outputs/{session_id}/bulk/`

## 2. File Path Updates

- [x] 2.1 Update `app.py` to use session-based output directory
- [x] 2.2 Update `pages/Bulk_Generation.py` to use session-based bulk directory
- [x] 2.3 Update `scripts/Elevenlabs_functions.py` to accept session-aware paths
- [x] 2.4 Ensure backward compatibility with existing file structure

## 3. Download Functionality

- [x] 3.1 Add download button to File Explorer for individual files
- [x] 3.2 Add bulk download (ZIP) functionality for session files
- [x] 3.3 Add download buttons to main page audio history
- [x] 3.4 Implement ZIP creation utility for bulk downloads
- [x] 3.5 Add download progress indicators

## 4. File Explorer Updates

- [x] 4.1 Filter File Explorer to show only current session's files
- [x] 4.2 Add session info display (session ID, file count, total size)
- [x] 4.3 Add download buttons next to each file
- [x] 4.4 Add "Download All" button for session files

## 5. Cleanup Mechanism

- [x] 5.1 Create cleanup utility function for old session directories
- [x] 5.2 Add configurable session timeout (default: 24 hours)
- [x] 5.3 Run cleanup on app startup
- [x] 5.4 Add cleanup on file operations (optional, to prevent accumulation)
- [ ] 5.5 Log cleanup operations for debugging

## 6. Testing & Documentation

- [x] 6.1 Write tests for session ID generation
- [x] 6.2 Write tests for session-based file paths
- [x] 6.3 Write tests for download functionality
- [x] 6.4 Write tests for cleanup mechanism
- [ ] 6.5 Update documentation with session-based file management
- [ ] 6.6 Add migration notes for existing deployments

