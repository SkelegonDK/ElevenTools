# TTS Generation Spec Changes

## REMOVED Requirements

### Requirement: Seed Management
**Reason**: Seed management adds unnecessary complexity to the user interface and codebase without providing significant value to most users. ElevenLabs' TTS API has evolved to provide more consistent results by default.
**Migration**: Users requiring reproducibility should rely on identical voice settings and text input rather than seed values.

The system SHALL provide seed management for reproducible audio generation results.

#### Scenario: Random seed generation
- **WHEN** user generates audio without specifying a seed
- **THEN** system generates a random seed and uses it for generation
- **AND** seed value is displayed and logged with the audio file

#### Scenario: Fixed seed usage
- **WHEN** user provides a specific seed value
- **THEN** system uses that seed for generation
- **AND** identical inputs with same seed produce identical audio output

#### Scenario: Seed persistence
- **WHEN** audio is generated with a seed
- **THEN** seed information is included in the filename and metadata
- **AND** users can reference the seed for future reproductions

## MODIFIED Requirements

### Requirement: Audio Output Management
The system SHALL manage generated audio files with proper naming, storage, and playback functionality.

#### Scenario: Audio file naming
- **WHEN** audio is generated
- **THEN** file is named using format: `LANGUAGE_VOICE_NAME_DATE_ID.mp3`
- **AND** filename ensures uniqueness and traceability

#### Scenario: Audio file storage
- **WHEN** audio is generated
- **THEN** file is stored in `outputs/single/` directory
- **AND** file metadata is preserved for file explorer access

#### Scenario: Immediate playback
- **WHEN** audio generation completes
- **THEN** system provides immediate audio playback controls
- **AND** playback works across different browsers and devices
