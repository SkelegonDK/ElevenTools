## Why
Currently, users must select OpenRouter models separately on each page (Translation page, main app page for enhancement). This creates friction and inconsistency. Converting the API Management page to a unified Settings page allows users to configure default models for translation and script enhancement in one place, improving UX and reducing repetitive model selection. The Settings page will serve as the central configuration hub for all application preferences.

## What Changes
- **BREAKING**: Rename `API_Management.py` to `Settings.py` (or `Settings.py` if multi-page)
- Convert API Management page to Settings page with multiple sections:
  - API Key Management (existing functionality)
  - Default Translation Model Selection (with same UI as Translation page)
  - Default Script Enhancement Model Selection (with same UI as Translation page)
- Set "minimax/minimax-m2:free" as default for both translation and enhancement models
- Add gear icon (⚙️) links to Settings page from Translation page and main app page
- Display warnings when default models are not configured before attempting translation/enhancement
- Store default model preferences in session state
- Update Translation page to use default model from settings if no page-specific selection
- Update main app page enhancement to use default model from settings if no page-specific selection
- Add comprehensive Playwright UI tests for Settings page functionality
- Update all documentation, error messages, and code references from "API Management" to "Settings"

## Impact
- Affected specs: 
  - `settings` (new capability - ADDED)
  - `translation` (MODIFIED - use default from settings)
  - `tts-generation` (MODIFIED - use default from settings for enhancement)
- Affected code:
  - `pages/API_Management.py` → `pages/Settings.py` (rename and extend)
  - `pages/3_Translation.py` - Add gear icon, use default from settings, update references
  - `app.py` - Add gear icon, use default from settings for enhancement, update references
  - `pages/Bulk_Generation.py` - Update API Management references to Settings
  - `scripts/openrouter_functions.py` - Helper functions for default model retrieval, update error messages
  - `utils/error_handling.py` - Update error messages referencing API Management
  - `tests/ui_tests/test_api_management_page.py` → `tests/ui_tests/test_settings_page.py` (rename and extend)
  - `README.md` - Update all API Management references to Settings
  - `openspec/project.md` - Update API Management reference to Settings
  - `tests/ui_tests/README.md` - Update test file reference

