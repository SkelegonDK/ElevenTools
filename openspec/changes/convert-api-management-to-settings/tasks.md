## 1. Settings Page Implementation
- [ ] 1.1 Rename `pages/API_Management.py` to `pages/Settings.py`
- [ ] 1.2 Update page title and icon to reflect Settings page (keep API management section)
- [ ] 1.3 Create reusable model selection component function that matches Translation page UI (fuzzy search, free filter, model display)
- [ ] 1.4 Add "Default Translation Model" section to Settings page using model selection component
- [ ] 1.5 Add "Default Script Enhancement Model" section to Settings page using model selection component
- [ ] 1.6 Initialize default models in session state: `default_translation_model` and `default_enhancement_model` to "minimax/minimax-m2:free"
- [ ] 1.7 Store selected default models in session state when user saves settings
- [ ] 1.8 Add visual indicator showing current default models in Settings page
- [ ] 1.9 Add warning messages in Settings page when models are not configured
- [ ] 1.10 Ensure API key management section remains functional and unchanged

## 2. Translation Page Updates
- [ ] 2.1 Add gear icon (⚙️) button/link near page title linking to Settings page
- [ ] 2.2 Update translation page to check for default model from settings (`st.session_state.default_translation_model`)
- [ ] 2.3 Use default model from settings if no page-specific model is selected
- [ ] 2.4 Display warning message when attempting translation without model configured (neither page-specific nor default)
- [ ] 2.5 Update model selection UI to show when using default from settings

## 3. Main App Page Updates
- [ ] 3.1 Add gear icon (⚙️) button/link near enhancement section linking to Settings page
- [ ] 3.2 Update enhancement function call to use default model from settings (`st.session_state.default_enhancement_model`) if no model specified
- [ ] 3.3 Display warning message when attempting enhancement without model configured
- [ ] 3.4 Update enhancement UI to indicate when using default from settings

## 4. Helper Functions
- [ ] 4.1 Create `get_default_translation_model()` helper function that returns default from session state or falls back to "minimax/minimax-m2:free"
- [ ] 4.2 Create `get_default_enhancement_model()` helper function that returns default from session state or falls back to "minimax/minimax-m2:free"
- [ ] 4.3 Update `enhance_script_with_openrouter()` to use default enhancement model if model_id is None
- [ ] 4.4 Update `translate_script()` to use default translation model if model is None

## 5. UI/UX Improvements
- [ ] 5.1 Ensure gear icons are visually consistent and clearly indicate settings access
- [ ] 5.2 Add tooltips to gear icons explaining they lead to settings for default model configuration
- [ ] 5.3 Ensure warning messages are clear and actionable (guide users to Settings page)
- [ ] 5.4 Test that Settings page model selection UI matches Translation page exactly (same components, same behavior)

## 6. Testing
- [ ] 6.1 Rename `tests/ui_tests/test_api_management_page.py` to `tests/ui_tests/test_settings_page.py`
- [ ] 6.2 Update existing API management tests to work with Settings page structure
- [ ] 6.3 Add Playwright test: Settings page loads with all sections visible
- [ ] 6.4 Add Playwright test: Default translation model selection works (fuzzy search, free filter)
- [ ] 6.5 Add Playwright test: Default enhancement model selection works (fuzzy search, free filter)
- [ ] 6.6 Add Playwright test: Default models persist in session state after selection
- [ ] 6.7 Add Playwright test: Translation page gear icon navigates to Settings
- [ ] 6.8 Add Playwright test: Main app page gear icon navigates to Settings
- [ ] 6.9 Add Playwright test: Warning displayed when attempting translation without model
- [ ] 6.10 Add Playwright test: Warning displayed when attempting enhancement without model
- [ ] 6.11 Add Playwright test: Default model is used when no page-specific selection made
- [ ] 6.12 Add Playwright test: Page-specific model selection overrides default from settings
- [ ] 6.13 Add Playwright test: Model selection UI conventions and UX practices (check for consistent styling, clear labels, helpful tooltips)

## 7. Documentation & References Update
- [ ] 7.1 Update README.md - Replace all "API Management" references with "Settings" (lines 49, 72, 89, 160)
- [ ] 7.2 Update error messages in `utils/error_handling.py` - Replace "API Management page" with "Settings page" (lines 87, 92)
- [ ] 7.3 Update error messages in `scripts/openrouter_functions.py` - Replace "API Management" with "Settings" (lines 34, 133, 191, 256)
- [ ] 7.4 Update `pages/Bulk_Generation.py` - Replace "API Management" references with "Settings" (lines 33, 48, 57)
- [ ] 7.5 Update `app.py` - Replace "API Management" references with "Settings" (lines 52, 67, 76)
- [ ] 7.6 Update `pages/3_Translation.py` - Replace "API Management page" with "Settings page" (line 20)
- [ ] 7.7 Update `openspec/project.md` - Replace "API Management page" with "Settings page" (line 51)
- [ ] 7.8 Update test file references in `tests/ui_tests/README.md` - Update test_api_management_page.py reference
- [ ] 7.9 Search for any sitemap or navigation configuration files and update API Management references
- [ ] 7.10 Search for any other documentation files (.md) and update API Management references
- [ ] 7.11 Verify all code comments mentioning "API Management" are updated to "Settings"
- [ ] 7.12 Run comprehensive search to ensure no references to "API Management" or "API_Management" remain (except in git history)

