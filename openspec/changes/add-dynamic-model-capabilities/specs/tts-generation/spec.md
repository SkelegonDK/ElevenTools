## MODIFIED Requirements

### Requirement: Model-Voice Setting Compatibility Validation
The system SHALL validate that voice settings are compatible with the selected model version before generating audio, ensuring correct payload construction and preventing API errors. Model capabilities SHALL be determined dynamically using a capability detection system rather than hardcoded checks.

#### Scenario: Dynamic speed parameter validation
- **WHEN** speed parameter is provided with any model
- **THEN** system checks model capabilities using `supports_speed(model_id)` function
- **AND** if model does not support speed, raises ValidationError with message indicating which models support speed
- **AND** audio generation does not proceed
- **AND** payload is never constructed with incompatible settings

#### Scenario: Speed parameter inclusion based on capabilities
- **WHEN** speed parameter is provided with a model that supports speed (determined dynamically)
- **THEN** system includes speed in voice_settings payload
- **AND** speed value is correctly formatted as float
- **AND** audio generation proceeds successfully

#### Scenario: Speed parameter exclusion when not supported
- **WHEN** speed parameter is None or not provided with any model
- **THEN** system excludes speed from voice_settings payload
- **AND** other voice settings are still included correctly

#### Scenario: Common voice settings compatibility across all models
- **WHEN** stability, similarity_boost, style, or use_speaker_boost are provided with any supported model
- **THEN** system includes these settings in voice_settings payload
- **AND** settings are correctly formatted with proper types (float for stability/similarity/style, bool for use_speaker_boost)
- **AND** audio generation proceeds successfully regardless of model type

#### Scenario: Payload structure verification
- **WHEN** audio generation is requested with any model
- **THEN** payload contains correct structure: text, model_id, voice_settings (with appropriate settings)
- **AND** voice_settings contains only compatible settings for the selected model
- **AND** compatibility is determined using dynamic capability checks

#### Scenario: Bulk generation model compatibility
- **WHEN** bulk generation is performed with voice settings dictionary
- **THEN** system validates model compatibility using dynamic capability checks before processing each row
- **AND** incompatible settings (e.g., speed with non-supporting models) are rejected with appropriate error messages
- **AND** compatible settings are correctly passed to generate_audio function

## ADDED Requirements

### Requirement: Dynamic Model Capability Detection
The system SHALL provide a capability detection system that determines which voice settings are supported by each model without hardcoded checks.

#### Scenario: Capability detection for speed support
- **WHEN** system needs to determine if a model supports speed
- **THEN** it calls `supports_speed(model_id)` function
- **AND** function checks against allow-list of known speed-supporting models
- **AND** function may use pattern matching as fallback for new models
- **AND** result is cached to avoid repeated API calls or computation

#### Scenario: Capability detection extensibility
- **WHEN** ElevenLabs adds a new model with speed support
- **THEN** system can be updated by adding model ID to allow-list or pattern matching rules
- **AND** no code changes required in validation or UI logic
- **AND** UI automatically shows speed control for new model

#### Scenario: UI adaptation to model capabilities
- **WHEN** user selects a model from the dropdown
- **THEN** UI checks model capabilities using `supports_speed(model_id)`
- **AND** speed slider is shown only if model supports speed
- **AND** speed slider help text dynamically reflects which models support speed
- **AND** UI updates immediately when model selection changes

#### Scenario: Capability information retrieval
- **WHEN** system needs full capability information for a model
- **THEN** it calls `get_model_capabilities(model_id)` function
- **AND** function returns dictionary with capability flags (e.g., `{"speed": True, "style": True}`)
- **AND** results are cached for performance
- **AND** function supports extensibility for future capabilities

