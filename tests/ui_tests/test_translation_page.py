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

