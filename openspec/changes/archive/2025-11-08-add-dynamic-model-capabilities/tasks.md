## 1. Model Capabilities System
- [x] 1.1 Create `utils/model_capabilities.py` module with capability detection functions
- [x] 1.2 Implement `get_model_capabilities(model_id: str) -> Dict[str, bool]` function
- [x] 1.3 Implement `supports_speed(model_id: str) -> bool` function using pattern matching or allow-list
- [x] 1.4 Create initial allow-list of models supporting speed (eleven_multilingual_v2, eleven_turbo_v2_5, eleven_flash_v2_5, eleven_v3, etc.)
- [x] 1.5 Add pattern-based fallback for future models (e.g., models with "multilingual" in name/ID)
- [x] 1.6 Add capability caching mechanism using `@st_cache` decorator

## 2. Update Core Functions
- [x] 2.1 Replace hardcoded speed check in `generate_audio()` with `supports_speed()` call
- [x] 2.2 Update validation error message to be dynamic based on model capabilities
- [x] 2.3 Update payload construction logic to use capability checks
- [x] 2.4 Update `bulk_generate_audio()` to use capability checks for speed validation (inherited through generate_audio)

## 3. Update UI Components
- [x] 3.1 Update `app.py` to use `supports_speed()` for showing/hiding speed slider
- [x] 3.2 Update speed slider help text to be dynamic based on selected model
- [x] 3.3 Update `pages/Bulk_Generation.py` to use `supports_speed()` for speed slider
- [x] 3.4 Update session state voice_settings assignment to use capability checks

## 4. Tests
- [x] 4.1 Add tests for `get_model_capabilities()` function
- [x] 4.2 Add tests for `supports_speed()` with various model IDs
- [x] 4.3 Update existing model compatibility tests to use new capability system
- [x] 4.4 Add tests for pattern-based capability detection
- [x] 4.5 Add tests for UI components showing/hiding based on capabilities (covered by existing tests)

## 5. Documentation
- [x] 5.1 Update function docstrings to reference capability system
- [x] 5.2 Add inline comments explaining capability detection logic
- [x] 5.3 Update README.md to mention dynamic model capability detection

