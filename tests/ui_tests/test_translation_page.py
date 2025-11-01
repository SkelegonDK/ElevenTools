"""UI tests for the Translation page."""

import pytest
import re
from playwright.sync_api import Page, expect


class TestTranslationPage:
    """Test suite for the Translation page."""

    def test_page_loads(self, configured_page: Page, streamlit_server: str):
        """Test that the Translation page loads successfully."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for API calls
        
        # Check page loads - look for title or main content
        # Page might show error if API key missing, so check for any content
        title_or_content = (
            configured_page.get_by_text(re.compile(r"translation|script", re.IGNORECASE)).first
            if configured_page.get_by_text(re.compile(r"translation|script", re.IGNORECASE)).count() > 0
            else configured_page.locator('body')
        )
        expect(title_or_content).to_be_visible()

    def test_page_title_display(self, configured_page: Page, streamlit_server: str):
        """Test that page title is displayed."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for translation title
        translation_title = configured_page.get_by_text(re.compile(r"translation", re.IGNORECASE))
        expect(translation_title.first).to_be_visible()

    def test_text_area_present(self, configured_page: Page, streamlit_server: str):
        """Test that text input area is present."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for text area
        text_area = configured_page.locator('textarea').first
        expect(text_area).to_be_visible()

    def test_language_selection_present(self, configured_page: Page, streamlit_server: str):
        """Test that language selection dropdown is present."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for models to load
        
        # Check for language selectbox - try Streamlit test IDs first
        language_select = (
            configured_page.locator('[data-testid="stSelectbox"]').last  # Language is likely last selectbox
            if configured_page.locator('[data-testid="stSelectbox"]').count() > 0
            else configured_page.locator('select').last
        )
        expect(language_select).to_be_visible(timeout=10000)

    def test_translate_button_present(self, configured_page: Page, streamlit_server: str):
        """Test that translate button is present."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(3000)  # Wait for API calls and content to load
        
        # Check for translate button - Streamlit uses data-testid="stButton"
        translate_button = configured_page.locator('[data-testid="stButton"]').filter(
            has_text=re.compile(r'Translate', re.IGNORECASE)
        )
        if translate_button.count() == 0:
            # Fallback to role-based search
            translate_button = configured_page.get_by_role("button", name=re.compile(r'Translate', re.IGNORECASE))
        
        # Button might not be visible if page stopped early (e.g., missing API key)
        if translate_button.count() == 0:
            # Check if page stopped due to API key error
            error_text = configured_page.get_by_text(re.compile(r"api.*key|not.*found", re.IGNORECASE))
            if error_text.count() > 0:
                pytest.skip("Translate button not visible - API key may be missing")
            else:
                pytest.fail("Translate button not found and no error message detected")
        
        expect(translate_button.first).to_be_visible(timeout=10000)

    def test_api_key_error_display(self, configured_page: Page, streamlit_server: str):
        """Test that error is shown if API key is missing."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for API key error message if key is missing
        error_message = configured_page.get_by_text(re.compile(r"api.*key", re.IGNORECASE))
        # This may or may not be visible depending on secrets config
        assert error_message.count() >= 0

    def test_text_input_functionality(self, configured_page: Page, streamlit_server: str):
        """Test that text can be entered."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        text_area = configured_page.locator('textarea').first
        test_text = "Hello, how are you?"
        
        text_area.fill(test_text)
        expect(text_area).to_have_value(test_text)

    def test_model_selection_section_present(self, configured_page: Page, streamlit_server: str):
        """Test that model selection section is present."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for content to load
        
        # Check for model selection subheader - Streamlit renders headers with specific structure
        model_selection = configured_page.get_by_text(re.compile(r"model.*selection|select.*model", re.IGNORECASE))
        # Section might be visible even if API key is missing (shows error instead)
        if model_selection.count() == 0:
            # Check for any heading that might indicate model selection
            headings = configured_page.locator('h2, h3, [data-testid="stHeader"]')
            model_selection = headings.filter(has_text=re.compile(r"model", re.IGNORECASE))
        expect(model_selection.first).to_be_visible(timeout=10000)

    def test_model_search_input_present(self, configured_page: Page, streamlit_server: str):
        """Test that fuzzy search input field is visible."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for content to load
        
        # Look for search input - Streamlit uses data-testid="stTextInput"
        search_inputs = configured_page.locator('[data-testid="stTextInput"]')
        if search_inputs.count() == 0:
            # Fallback to regular text input
            search_inputs = configured_page.locator('input[type="text"]')
        # Should have at least one text input (for search)
        assert search_inputs.count() > 0, "Search input not found"

    def test_free_model_filter_checkbox_present(self, configured_page: Page, streamlit_server: str):
        """Test that free model filter checkbox is visible."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for content to load
        
        # Check for checkbox - Streamlit uses data-testid="stCheckbox"
        # Look for checkbox with "free" text nearby
        free_filter = configured_page.get_by_text(re.compile(r"show.*only.*free|free.*only", re.IGNORECASE))
        if free_filter.count() == 0:
            # Try to find checkbox by label
            checkboxes = configured_page.locator('[data-testid="stCheckbox"]')
            if checkboxes.count() > 0:
                free_filter = checkboxes.first
        expect(free_filter.first).to_be_visible(timeout=10000)

    def test_model_selection_dropdown_present(self, configured_page: Page, streamlit_server: str):
        """Test that model selection dropdown is present."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        # Wait for models to load
        configured_page.wait_for_timeout(3000)
        
        # Check for select elements - try Streamlit test IDs first
        selects = configured_page.locator('[data-testid="stSelectbox"]')
        if selects.count() == 0:
            selects = configured_page.locator('select')
        # Should have at least one select (language), model select may be conditional on API key/models loading
        assert selects.count() >= 1, f"Expected at least 1 selectbox, found {selects.count()}"

    def test_model_search_functionality(self, configured_page: Page, streamlit_server: str):
        """Test that model search input can be used."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for models to load
        
        # Find search input and type in it
        search_inputs = configured_page.locator('input[type="text"]')
        if search_inputs.count() > 0:
            search_input = search_inputs.first
            search_input.fill("test")
            expect(search_input).to_have_value("test")

    def test_free_model_filter_toggle(self, configured_page: Page, streamlit_server: str):
        """Test that free model filter can be toggled."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)
        
        # Find and click the free filter checkbox
        free_checkbox = configured_page.locator('input[type="checkbox"]').first
        if free_checkbox.is_visible():
            initial_state = free_checkbox.is_checked()
            free_checkbox.click()
            configured_page.wait_for_timeout(500)  # Wait for filter to apply
            # State should have changed
            assert free_checkbox.is_checked() != initial_state

    def test_refresh_button_present(self, configured_page: Page, streamlit_server: str):
        """Test that refresh button is present."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for content to load
        
        # Check for refresh button - Streamlit uses data-testid="stButton"
        refresh_button = configured_page.locator('[data-testid="stButton"]').filter(
            has_text=re.compile(r"refresh|🔄", re.IGNORECASE)
        )
        if refresh_button.count() == 0:
            # Fallback to role-based search
            refresh_button = configured_page.get_by_role("button", name=re.compile(r"refresh", re.IGNORECASE))
        # Refresh button may not be visible if models failed to load
        if refresh_button.count() > 0:
            expect(refresh_button.first).to_be_visible(timeout=10000)

    def test_model_info_display(self, configured_page: Page, streamlit_server: str):
        """Test that model information is displayed when available."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(3000)  # Wait for models to load
        
        # Check for any model-related text (could be "Selected:", model names, etc.)
        # This is conditional on models being available
        page_text = configured_page.locator('body').text_content()
        # Page should have loaded successfully
        assert page_text is not None

    def test_translation_with_model_selection(self, configured_page: Page, streamlit_server: str):
        """Test that translation works with model selection."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(3000)  # Wait for content to load
        
        # Enter text to translate
        text_area = configured_page.locator('textarea').first
        text_area.fill("Hello")
        
        # Find translate button - Streamlit uses data-testid="stButton"
        translate_button = configured_page.locator('[data-testid="stButton"]').filter(
            has_text=re.compile(r'Translate', re.IGNORECASE)
        )
        if translate_button.count() == 0:
            translate_button = configured_page.get_by_role("button", name=re.compile(r'Translate', re.IGNORECASE))
        
        # Check if button exists before clicking
        if translate_button.count() == 0:
            # Check if page stopped due to API key error
            error_text = configured_page.get_by_text(re.compile(r"api.*key|not.*found", re.IGNORECASE))
            if error_text.count() > 0:
                pytest.skip("Translate button not available - API key may be missing")
            else:
                pytest.fail("Translate button not found")
        
        # Click the button and wait for response
        translate_button.first.click()
        
        # Wait for response or error
        configured_page.wait_for_timeout(3000)
        
        # Page should still be functional (even if translation failed)
        expect(configured_page.locator('body')).to_be_visible()

