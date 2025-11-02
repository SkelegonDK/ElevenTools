## Why
ElevenLabs v3 models support Audio Tags ([excited], [whispers], [sighs], etc.) which provide more expressive and natural-sounding speech generation compared to the traditional `<break>` and `<emotional context>` tags. The current script enhancement feature uses generic prompting techniques that don't leverage v3's Audio Tags capabilities, resulting in suboptimal enhancement when v3 models are selected.

## What Changes
- Add model-aware enhancement that detects when v3 model (`eleven_v3`) is selected
- Create v3-specific enhancement prompt that focuses on Audio Tags instead of traditional tags
- Extend `model_capabilities.py` to detect v3 model support
- Update enhancement function to route to v3-specific logic when appropriate
- Provide user feedback indicating when v3-specific enhancement is being used

## Impact
- Affected specs: `tts-generation` (script enhancement requirement)
- Affected code: 
  - `scripts/openrouter_functions.py` (enhancement logic)
  - `utils/model_capabilities.py` (v3 detection)
  - `app.py` (model selection context)

