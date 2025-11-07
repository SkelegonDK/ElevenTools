## ADDED Requirements

### Requirement: Path Traversal Prevention
The system SHALL sanitize and validate all user-controlled file paths to prevent directory traversal attacks.

#### Scenario: CSV filename sanitization
- **WHEN** a CSV file is uploaded for bulk generation
- **THEN** the filename is sanitized to remove path separators and dangerous characters
- **AND** the sanitized filename is validated before use in path construction
- **AND** path traversal sequences (../, ..\\) are prevented

#### Scenario: Output directory path validation
- **WHEN** output directory paths are constructed from user input
- **THEN** paths are validated to ensure they remain within the intended output directory
- **AND** absolute paths or paths containing traversal sequences are rejected

#### Scenario: Filesystem entry validation
- **WHEN** filesystem entries from `os.listdir()` are used in path construction
- **THEN** entries are validated before use
- **AND** only expected file types and safe filenames are processed

### Requirement: Input Validation and Size Limits
The system SHALL validate all user inputs and enforce size limits to prevent DoS attacks and resource exhaustion.

#### Scenario: CSV file size validation
- **WHEN** a CSV file is uploaded
- **THEN** the file size is validated against a maximum limit (10MB)
- **AND** files exceeding the limit are rejected with an error message

#### Scenario: DataFrame row limit validation
- **WHEN** a CSV file is processed into a DataFrame
- **THEN** the number of rows is validated against a maximum limit (1000 rows)
- **AND** DataFrames exceeding the limit are rejected with an error message

#### Scenario: Column name validation
- **WHEN** CSV column names are processed
- **THEN** column names are validated to contain only alphanumeric characters and underscores
- **AND** invalid column names are rejected with an error message

#### Scenario: Text input length validation
- **WHEN** user text input is processed for script enhancement or translation
- **THEN** text length is validated against a maximum limit (10,000 characters)
- **AND** text exceeding the limit is rejected with an error message

### Requirement: Content Escaping and XSS Prevention
The system SHALL escape all user-controlled content before rendering to prevent cross-site scripting attacks.

#### Scenario: User script content escaping
- **WHEN** user-provided script content is displayed in the UI
- **THEN** HTML special characters are escaped before rendering
- **AND** script tags and other dangerous HTML are neutralized

#### Scenario: Enhanced script display
- **WHEN** enhanced script content from OpenRouter API is displayed
- **THEN** content is escaped before rendering
- **AND** user-controlled variables in scripts are escaped

#### Scenario: Filename display
- **WHEN** filenames containing user-controlled content are displayed
- **THEN** filenames are escaped before rendering
- **AND** path information is not exposed in error messages

### Requirement: Secure File Path Construction
The system SHALL construct file paths securely using validated and sanitized components.

#### Scenario: Output path construction
- **WHEN** output file paths are constructed
- **THEN** all path components are sanitized before joining
- **AND** final paths are validated to ensure they remain within intended directories
- **AND** absolute paths are normalized to relative paths within the output directory

#### Scenario: Bulk generation directory creation
- **WHEN** bulk generation creates output directories from CSV filenames
- **THEN** directory names are sanitized and validated
- **AND** directory creation is restricted to the outputs directory tree

## MODIFIED Requirements

### Requirement: File Upload Security
The system SHALL validate file uploads for size, type, and content before processing.

#### Scenario: CSV file upload validation
- **WHEN** a CSV file is uploaded
- **THEN** file size, type, and content are validated
- **AND** invalid files are rejected with clear error messages
- **AND** file processing respects configured size limits

### Requirement: User Input Processing
The system SHALL validate and sanitize all user inputs before processing or storage.

#### Scenario: Script input validation
- **WHEN** user provides script text for processing
- **THEN** text length and content are validated
- **AND** invalid input is rejected with error messages
- **AND** valid input is sanitized before processing

