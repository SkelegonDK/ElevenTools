# Bulk Generation Spec Changes

## REMOVED Requirements

### Requirement: Seed Management Across Batch
**Reason**: Seed management adds unnecessary complexity without providing significant value. Modern ElevenLabs API provides consistent results without manual seed control.
**Migration**: Users should rely on consistent voice settings and text input for reproducible results.

The system SHALL execute bulk generation with seed management for batch processing.

#### Scenario: Seed management across batch
- **WHEN** user configures seed settings for batch
- **THEN** system supports both random seeds per file and fixed seed across batch
- **AND** logs seed information for each generated file

## MODIFIED Requirements

### Requirement: Batch Processing Engine
The system SHALL execute bulk generation with parallel processing, progress tracking, and error handling.

#### Scenario: Parallel audio generation
- **WHEN** bulk generation is initiated
- **THEN** system processes multiple rows in parallel to improve performance
- **AND** manages API rate limits and resource constraints

#### Scenario: Progress tracking and feedback
- **WHEN** bulk generation is running
- **THEN** system displays real-time progress with completed/total counts
- **AND** shows current processing status and estimated completion time

### Requirement: Batch Output Organization
The system SHALL organize bulk generation outputs with proper file structure and naming conventions.

#### Scenario: Output directory structure
- **WHEN** bulk generation completes
- **THEN** system creates output directory named after source CSV file
- **AND** stores all generated files in `outputs/{CSV_FILENAME}/` directory

#### Scenario: File naming convention
- **WHEN** individual audio files are generated in batch
- **THEN** system names files using format from filename column or auto-generated names
- **AND** ensures all filenames are unique and filesystem-safe

#### Scenario: Metadata preservation
- **WHEN** bulk generation creates files
- **THEN** system preserves generation metadata (voice, settings, source row)
- **AND** creates manifest file with batch generation details
