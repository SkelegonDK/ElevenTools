# Remove Seed Settings

## Why

The current seed management functionality adds complexity to the user interface and codebase without providing significant value to most users. ElevenLabs' TTS API has evolved to provide more consistent results by default, making manual seed management less critical for reproducibility. The seed settings create UI clutter and maintenance overhead while serving a niche use case that could be addressed through other means if needed.

## What Changes

- Remove seed management UI components from main app and bulk generation pages
- Remove seed-related parameters from audio generation functions
- Remove seed-related session state management
- Remove seed information from file naming conventions
- Remove seed-related documentation and help text
- **BREAKING**: Generated audio files will no longer include seed values in filenames
- **BREAKING**: Reproducibility through fixed seeds will no longer be available

## Impact

- Affected specs: `tts-generation`, `bulk-generation`
- Affected code: `app.py`, `pages/Bulk_Generation.py`, `scripts/Elevenlabs_functions.py`
- Simplified user interface with reduced cognitive load
- Reduced codebase complexity and maintenance burden
- Breaking change for users relying on seed-based reproducibility
- File naming convention changes from `LANGUAGE_VOICE_NAME_DATE_ID_SEED.mp3` to `LANGUAGE_VOICE_NAME_DATE_ID.mp3`
