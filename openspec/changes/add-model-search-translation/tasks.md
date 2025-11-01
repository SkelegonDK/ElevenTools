## 1. Implementation
- [ ] 1.1 Add `fetch_openrouter_models()` function to `scripts/openrouter_functions.py` to retrieve available models from OpenRouter API
- [ ] 1.2 Parse and identify free models from API response (check pricing.prompt=0 and pricing.completion=0 for zero cost)
- [ ] 1.3 Add `search_models_fuzzy()` function for fuzzy model search using Python's `difflib` or `fuzzywuzzy` library
- [ ] 1.4 Add `filter_free_models()` function to filter models by free status
- [ ] 1.5 Update `translate_script_with_openrouter()` to accept optional `model` parameter (default to "openrouter/auto" for backward compatibility)
- [ ] 1.6 Update `Translation_functions.py` `translate_script()` to accept and pass model parameter
- [ ] 1.7 Add `@st.cache_data(ttl=3600)` decorated function to Translation page for model fetching and caching (follow Streamlit caching best practices)
- [ ] 1.8 Initialize session state variables: `selected_model`, `model_search_query`, `show_free_only` with appropriate defaults
- [ ] 1.9 Add `st.text_input` for fuzzy search with `key="model_search_query"` and `on_change` callback to update filtered results
- [ ] 1.10 Add `st.checkbox` or `st.toggle` for free model filter with `key="show_free_only"` and `on_change` callback
- [ ] 1.11 Create callback function `update_filtered_models()` that combines fuzzy search and free filter logic
- [ ] 1.12 Add `st.selectbox` for model selection with filtered options, `key="selected_model"`, and optional `on_change` callback
- [ ] 1.13 Update Translation page to read `st.session_state.selected_model` and pass to translation function
- [ ] 1.14 Add error handling for model fetching failures with fallback to default model using try/except
- [ ] 1.15 Add manual refresh button with `st.cache_data.clear()` functionality to refresh model cache

## 2. Unit Testing
- [ ] 2.1 Create `tests/test_api/test_openrouter_model_functions.py` for model-related functions
- [ ] 2.2 Add unit test `test_fetch_openrouter_models_success()` - mock successful API response with sample models, verify caching decorator applied
- [ ] 2.3 Add unit test `test_fetch_openrouter_models_api_error()` - test error handling for API failures
- [ ] 2.4 Add unit test `test_fetch_openrouter_models_empty_response()` - test empty response handling
- [ ] 2.5 Add unit test `test_fetch_openrouter_models_caching()` - verify `@st.cache_data` caching behavior with mock
- [ ] 2.6 Add unit test `test_identify_free_models()` - verify free model identification from API response (check pricing.prompt=0 and pricing.completion=0)
- [ ] 2.7 Add unit test `test_identify_free_models_mixed_pricing()` - test with models having various pricing structures
- [ ] 2.8 Add unit test `test_filter_free_models()` - verify filtering logic returns only free models
- [ ] 2.9 Add unit test `test_search_models_fuzzy_exact_match()` - test exact model name matching
- [ ] 2.10 Add unit test `test_search_models_fuzzy_partial_match()` - test partial name matching
- [ ] 2.11 Add unit test `test_search_models_fuzzy_typo_tolerance()` - test fuzzy matching with typos
- [ ] 2.12 Add unit test `test_search_models_fuzzy_case_insensitive()` - test case-insensitive matching
- [ ] 2.13 Add unit test `test_search_models_fuzzy_empty_query()` - test behavior with empty search query
- [ ] 2.14 Add unit test `test_combined_fuzzy_search_and_free_filter()` - verify both filters work together
- [ ] 2.15 Add unit test `test_session_state_initialization()` - verify session state variables initialized correctly
- [ ] 2.16 Add unit test `test_translate_with_custom_model()` - integration test for translation with selected model
- [ ] 2.17 Add unit test `test_translate_with_default_model()` - verify backward compatibility

## 3. Playwright UI Testing
- [ ] 3.1 Update `tests/ui_tests/test_translation_page.py` with new model selection tests
- [ ] 3.2 Add Playwright test `test_model_list_fetched_on_load()` - verify models are fetched and displayed when page loads, check for cached data
- [ ] 3.3 Add Playwright test `test_model_search_input_present()` - verify `st.text_input` for fuzzy search is visible with correct key
- [ ] 3.4 Add Playwright test `test_fuzzy_search_filters_models()` - enter search query, verify `on_change` callback triggers, filtered results appear
- [ ] 3.5 Add Playwright test `test_fuzzy_search_real_time_updates()` - verify results update as user types (test widget callback behavior)
- [ ] 3.6 Add Playwright test `test_search_query_session_state()` - verify search query persists in session state after input
- [ ] 3.7 Add Playwright test `test_free_model_filter_checkbox_present()` - verify free filter `st.checkbox`/`st.toggle` is visible with correct key
- [ ] 3.8 Add Playwright test `test_free_model_filter_toggle()` - toggle free filter, verify `on_change` callback, only free models shown
- [ ] 3.9 Add Playwright test `test_free_filter_session_state()` - verify filter state persists in `st.session_state.show_free_only`
- [ ] 3.10 Add Playwright test `test_free_filter_combined_with_search()` - enable free filter, then search, verify both filters apply correctly
- [ ] 3.11 Add Playwright test `test_model_selection_dropdown()` - verify `st.selectbox` for model selection is functional with filtered options
- [ ] 3.12 Add Playwright test `test_model_selection_session_state()` - verify selected model stored in `st.session_state.selected_model`
- [ ] 3.13 Add Playwright test `test_model_selection_persists()` - select model, navigate away and back, verify model persists in session state
- [ ] 3.14 Add Playwright test `test_model_used_for_translation()` - select model, translate text, verify selected model passed to translation function
- [ ] 3.15 Add Playwright test `test_model_fetch_error_display()` - mock API failure, verify error message displays gracefully with fallback
- [ ] 3.16 Add Playwright test `test_default_model_when_none_selected()` - verify default "openrouter/auto" used when no selection
- [ ] 3.17 Add Playwright test `test_model_cache_refresh()` - verify manual refresh button clears cache using `st.cache_data.clear()` and updates list

## 4. Validation
- [ ] 4.1 Run all unit tests: `uv run pytest tests/test_api/test_openrouter_model_functions.py -v`
- [ ] 4.2 Run all Playwright UI tests: `uv run pytest tests/ui_tests/test_translation_page.py -v`
- [ ] 4.3 Verify fuzzy search works with partial model names
- [ ] 4.4 Verify free model filter correctly identifies and displays only free models
- [ ] 4.5 Verify free filter and fuzzy search work together correctly
- [ ] 4.6 Verify model selection persists during translation session
- [ ] 4.7 Verify backward compatibility (default model used when none selected)
- [ ] 4.8 Verify caching prevents excessive API calls
- [ ] 4.9 Verify test coverage meets project standards (aim for >80% coverage)
- [ ] 4.10 Run `openspec validate add-model-search-translation --strict` and resolve issues

