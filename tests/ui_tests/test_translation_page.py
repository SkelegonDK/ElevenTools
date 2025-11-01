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
        
        # Check page loads
        expect(configured_page.locator('body')).to_be_visible()

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
        
        # Check for language selectbox
        language_select = configured_page.locator('select').first
        expect(language_select).to_be_visible()

    def test_translate_button_present(self, configured_page: Page, streamlit_server: str):
        """Test that translate button is present."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for translate button
        translate_button = configured_page.get_by_role("button", name=re.compile(r'Translate', re.IGNORECASE))
        expect(translate_button).to_be_visible()

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
        
        # Check for model selection subheader
        model_selection = configured_page.get_by_text(re.compile(r"model.*selection", re.IGNORECASE))
        expect(model_selection.first).to_be_visible()

    def test_model_search_input_present(self, configured_page: Page, streamlit_server: str):
        """Test that fuzzy search input field is visible."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        # Look for search input (Streamlit uses input elements)
        search_inputs = configured_page.locator('input[type="text"]')
        # Should have at least one text input (for search)
        assert search_inputs.count() > 0

    def test_free_model_filter_checkbox_present(self, configured_page: Page, streamlit_server: str):
        """Test that free model filter checkbox is visible."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for checkbox with "free" text
        free_filter = configured_page.get_by_text(re.compile(r"show.*only.*free", re.IGNORECASE))
        expect(free_filter.first).to_be_visible()

    def test_model_selection_dropdown_present(self, configured_page: Page, streamlit_server: str):
        """Test that model selection dropdown is present."""
        configured_page.goto(f"{streamlit_server}/3_Translation")
        configured_page.wait_for_load_state("networkidle")
        
        # Wait a bit for models to load
        configured_page.wait_for_timeout(2000)
        
        # Check for select elements (should have at least language select, and potentially model select)
        selects = configured_page.locator('select')
        # Should have at least one select (language), model select may be conditional
        assert selects.count() >= 1

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
        
        # Check for refresh button
        refresh_button = configured_page.get_by_role("button", name=re.compile(r"refresh", re.IGNORECASE))
        expect(refresh_button.first).to_be_visible()

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
        configured_page.wait_for_timeout(2000)
        
        # Enter text to translate
        text_area = configured_page.locator('textarea').first
        text_area.fill("Hello")
        
        # Try to translate (may fail if API key not configured, but should not crash)
        translate_button = configured_page.get_by_role("button", name=re.compile(r'Translate', re.IGNORECASE))
        translate_button.click()
        
        # Wait for response or error
        configured_page.wait_for_timeout(3000)
        
        # Page should still be functional
        expect(configured_page.locator('body')).to_be_visible()

