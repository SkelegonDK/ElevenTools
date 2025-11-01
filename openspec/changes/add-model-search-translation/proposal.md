## Why
Users currently cannot select OpenRouter models for translation - the system hardcodes "openrouter/auto" as the default model. This limits user control over translation quality, cost, and performance. Adding fuzzy search-based model selection enables users to discover and choose from available OpenRouter models, improving translation customization and allowing cost/quality trade-offs.

## What Changes
- Add OpenRouter models API integration to fetch available models
- Implement fuzzy search functionality for model discovery and selection
- Add free model filter option to show only models with zero cost
- Add model selection UI component to Translation page with search capability and free model filter
- Update translation functions to accept and use selected model parameter
- Enhance model selection requirement in translation spec with fuzzy search scenarios and free model filtering
- Add comprehensive unit tests for model fetching, filtering, and search functions
- Add Playwright UI tests for model selection, search, and filtering workflows

## Impact
- Affected specs: `translation` (modifies existing model selection requirement, adds fuzzy search capability)
- Affected code: 
  - `scripts/openrouter_functions.py` - Add model fetching and fuzzy search functions
  - `scripts/Translation_functions.py` - Add model parameter support
  - `pages/3_Translation.py` - Add model selection UI with fuzzy search and free filter

## Implementation Notes
- Use `@st.cache_data(ttl=3600)` for model fetching to cache API responses (min 1 hour TTL)
- Use `st.session_state` to persist selected model and filter states across reruns
- Implement real-time filtering using `on_change` callbacks on search input widgets
- Follow Streamlit best practices for widget state management and callback patterns

