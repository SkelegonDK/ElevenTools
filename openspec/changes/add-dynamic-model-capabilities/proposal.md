## Why
The current implementation hardcodes model capability checks (e.g., speed support only for `eleven_multilingual_v2`), making it inflexible when ElevenLabs adds new models or extends capabilities to existing models. This requires manual code updates in multiple places (validation logic, UI components, bulk generation) whenever model capabilities change. A dynamic capability detection system would automatically adapt to new models and their supported settings without code changes.

## What Changes
- Create a model capabilities system that dynamically determines which voice settings each model supports
- Replace hardcoded model checks with capability-based validation
- Make UI components (speed slider, settings controls) adapt based on selected model capabilities
- Implement pattern-based or allow-list approach for model capability detection
- Update validation logic in `generate_audio()` to use dynamic capability checks
- Update UI in `app.py` and `pages/Bulk_Generation.py` to show/hide controls dynamically
- Add configuration mechanism for model capabilities (allow-list or pattern matching)
- Maintain backward compatibility with existing models

## Impact
- Affected specs: `tts-generation`
- Affected code: 
  - `scripts/Elevenlabs_functions.py` - Replace hardcoded checks with capability functions
  - `app.py` - Dynamic UI based on model capabilities
  - `pages/Bulk_Generation.py` - Dynamic UI based on model capabilities
  - `utils/` - New model capabilities utility module
- Benefits:
  - Automatic support for new models with speed capability
  - Single source of truth for model capabilities
  - Easier maintenance when ElevenLabs adds new models
  - Future-proof architecture for additional voice settings

