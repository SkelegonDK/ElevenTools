## Why
The current test suite validates individual voice settings (e.g., speed parameter validation) but lacks comprehensive tests to verify that voice model versions are compatible with the correct voice settings combinations. Based on ElevenLabs API documentation and MCP verification, the system currently restricts speed parameter to `eleven_multilingual_v2` only, while other settings (stability, similarity_boost, style, use_speaker_boost) should work with all models. Comprehensive tests will prevent runtime errors and ensure correct payload construction.

## What Changes
- Add test suite to verify model-voice setting compatibility
- Test that speed parameter validation correctly rejects non-multilingual-v2 models (current implementation behavior)
- Test that speed parameter is correctly included in payload for multilingual v2 when provided
- Test that speed parameter is correctly excluded from payload for non-multilingual models
- Test that all common voice settings (stability, similarity_boost, style, use_speaker_boost) work correctly with all supported models
- Verify payload construction includes correct settings for each model type
- Test bulk generation respects model-voice setting compatibility

## Impact
- Affected specs: `tts-generation`
- Affected code: `tests/test_api/test_elevenlabs_functions.py`
- Adds comprehensive test coverage for model-voice setting compatibility to prevent API errors and ensure correct behavior across different ElevenLabs models
- **Note**: Current implementation only checks for `eleven_multilingual_v2` for speed support. Tests will verify this behavior; future work may need to extend support to other models (eleven_turbo_v2_5, eleven_flash_v2_5, eleven_v3) if they also support speed.

