## MODIFIED Requirements

### Requirement: Session-Based File Organization
The system SHALL organize generated files by user session to ensure privacy and isolation between users.

#### Scenario: Session directory creation
- **WHEN** a user generates their first audio file
- **THEN** a unique session directory is created: `outputs/{session_id}/single/` or `outputs/{session_id}/bulk/`
- **AND** the session ID is stored in session state for subsequent operations

#### Scenario: Session isolation
- **WHEN** a user accesses the File Explorer
- **THEN** only files from their current session are displayed
- **AND** files from other sessions are not accessible

#### Scenario: Session persistence
- **WHEN** a user navigates between pages
- **THEN** their session ID persists in session state
- **AND** files remain accessible across page navigations

### Requirement: File Download Functionality
The system SHALL provide download capabilities for generated audio files.

#### Scenario: Individual file download
- **WHEN** a user views a generated audio file
- **THEN** a download button is displayed next to the file
- **AND** clicking the button downloads the file with its original filename

#### Scenario: Bulk download
- **WHEN** a user wants to download multiple files from their session
- **THEN** a "Download All" button is available
- **AND** clicking the button creates a ZIP archive containing all session files
- **AND** the ZIP file is downloaded with a descriptive name

#### Scenario: Download from File Explorer
- **WHEN** a user views files in the File Explorer
- **THEN** each file has an individual download button
- **AND** bulk download options are available for bulk generation groups

### Requirement: Automatic File Cleanup
The system SHALL automatically clean up old session directories to prevent storage accumulation.

#### Scenario: Cleanup on startup
- **WHEN** the application starts
- **THEN** session directories older than the configured timeout (default: 24 hours) are removed
- **AND** cleanup operations are logged for debugging

#### Scenario: Configurable cleanup timeout
- **WHEN** cleanup runs
- **THEN** the timeout period is configurable via environment variable
- **AND** defaults to 24 hours if not configured

#### Scenario: Active session preservation
- **WHEN** cleanup runs
- **THEN** directories with recent file modifications are preserved
- **AND** only truly inactive session directories are removed

## ADDED Requirements

### Requirement: Session Management Utilities
The system SHALL provide utilities for managing user sessions and session-based file operations.

#### Scenario: Session ID generation
- **WHEN** a new session is detected
- **THEN** a unique session ID is generated using UUID
- **AND** the session ID is stored in session state

#### Scenario: Session directory access
- **WHEN** file operations are performed
- **THEN** files are stored in the session-specific directory
- **AND** paths are validated to ensure they remain within the session directory

### Requirement: Download Progress and Feedback
The system SHALL provide clear feedback during download operations.

#### Scenario: Download button states
- **WHEN** a download is initiated
- **THEN** the button shows loading state
- **AND** provides success feedback after completion

#### Scenario: Large file handling
- **WHEN** downloading large files or ZIP archives
- **THEN** progress indicators are shown
- **AND** users are informed of download size

