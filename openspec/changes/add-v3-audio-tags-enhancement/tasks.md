## 1. Model Detection
- [x] 1.1 Add `supports_audio_tags()` function to `utils/model_capabilities.py` to detect v3 models
- [x] 1.2 Add v3 model IDs to allow-list (eleven_v3, eleven_multilingual_v3 if applicable)
- [x] 1.3 Update `get_model_capabilities()` to include audio_tags capability

## 2. V3 Enhancement Function
- [x] 2.1 Create `enhance_script_for_v3()` function in `scripts/openrouter_functions.py`
- [x] 2.2 Implement v3-specific prompt that emphasizes Audio Tags:
  - Emotions: [excited], [sad], [angry], [happily], [sorrowful]
  - Delivery: [whispers], [shouts], [x accent]
  - Human reactions: [laughs], [clears throat], [sighs]
  - Sound effects: [gunshot], [clapping], [explosion] (when contextually appropriate)
- [x] 2.3 Ensure Audio Tags are wrapped in square brackets per v3 specification
- [x] 2.4 Update prompt to explain Audio Tags format and when to use them

## 3. Model-Aware Routing
- [x] 3.1 Modify `enhance_script_with_openrouter()` to accept model_id parameter
- [x] 3.2 Add logic to route to v3-specific enhancement when v3 model detected
- [x] 3.3 Pass selected model_id from `app.py` to enhancement function
- [x] 3.4 Maintain backward compatibility for non-v3 models

## 4. User Interface Updates
- [x] 4.1 Add indicator in UI when v3-specific enhancement is active
- [x] 4.2 Update enhancement prompt help text to mention Audio Tags for v3 models
- [x] 4.3 Show example Audio Tags in help text or tooltip

## 5. Testing
- [x] 5.1 Add unit tests for `supports_audio_tags()` function
- [x] 5.2 Add tests for v3 enhancement prompt generation
- [x] 5.3 Add integration tests for model-aware routing
- [x] 5.4 Test backward compatibility with non-v3 models
- [x] 5.5 Verify Audio Tags format validation in enhanced output

