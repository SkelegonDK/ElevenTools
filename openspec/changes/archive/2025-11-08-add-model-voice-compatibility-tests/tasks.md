## 1. Test Implementation
- [x] 1.1 Add test function `test_speed_validation_for_monolingual_v1()` - verify ValidationError is raised when speed is provided with eleven_monolingual_v1
- [x] 1.2 Add test function `test_speed_validation_for_other_models()` - verify ValidationError is raised when speed is provided with other non-multilingual models (test at least one additional model)
- [x] 1.3 Add test function `test_multilingual_v2_speed_inclusion()` - verify speed is included in voice_settings payload for eleven_multilingual_v2 when provided
- [x] 1.4 Add test function `test_multilingual_v2_speed_exclusion()` - verify speed is excluded from payload for eleven_multilingual_v2 when not provided (None)
- [x] 1.5 Add test function `test_monolingual_v1_no_speed_in_payload()` - verify speed is never included in payload for monolingual v1 even if passed
- [x] 1.6 Add test function `test_common_settings_all_models()` - verify common voice settings (stability, similarity_boost, style, use_speaker_boost) are included in payload for all models
- [x] 1.7 Add test function `test_payload_structure_per_model()` - verify complete payload structure is correct for different model types
- [x] 1.8 Add test function `test_bulk_generation_model_compatibility()` - verify bulk generation respects model-voice setting compatibility (speed validation in bulk context)

## 2. Test Coverage Validation
- [x] 2.1 Run test suite and verify all new tests pass
- [x] 2.2 Verify test coverage includes all supported model types
- [x] 2.3 Verify edge cases are covered (boundary values, None values, etc.)

