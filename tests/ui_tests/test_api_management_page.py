"""UI tests for the API Management page."""

import pytest
import re
from playwright.sync_api import Page, expect


class TestAPIManagementPage:
    """Test suite for the API Management page."""

    def test_page_loads(self, configured_page: Page, streamlit_server: str):
        """Test that the API Management page loads successfully."""
        configured_page.goto(f"{streamlit_server}/API_Management")
        configured_page.wait_for_load_state("networkidle")
        
        # Check page loads
        expect(configured_page.locator('body')).to_be_visible()

    def test_page_title_display(self, configured_page: Page, streamlit_server: str):
        """Test that page title is displayed."""
        configured_page.goto(f"{streamlit_server}/API_Management")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for API Management title
        api_title = configured_page.get_by_text(re.compile(r"api.*management", re.IGNORECASE))
        expect(api_title.first).to_be_visible()

    def test_api_keys_section_present(self, configured_page: Page, streamlit_server: str):
        """Test that API keys section is present."""
        configured_page.goto(f"{streamlit_server}/API_Management")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for API keys header
        api_keys_header = configured_page.get_by_text(re.compile(r"api.*key", re.IGNORECASE))
        expect(api_keys_header.first).to_be_visible()

    def test_elevenlabs_api_key_status(self, configured_page: Page, streamlit_server: str):
        """Test that ElevenLabs API key status is displayed."""
        configured_page.goto(f"{streamlit_server}/API_Management")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for ElevenLabs status
        elevenlabs_status = configured_page.get_by_text(re.compile(r"elevenlabs", re.IGNORECASE))
        expect(elevenlabs_status.first).to_be_visible()

    def test_openrouter_api_key_status(self, configured_page: Page, streamlit_server: str):
        """Test that OpenRouter API key status is displayed."""
        configured_page.goto(f"{streamlit_server}/API_Management")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for OpenRouter status
        openrouter_status = configured_page.get_by_text(re.compile(r"openrouter", re.IGNORECASE))
        expect(openrouter_status.first).to_be_visible()

    def test_info_message_present(self, configured_page: Page, streamlit_server: str):
        """Test that info message about API keys is displayed."""
        configured_page.goto(f"{streamlit_server}/API_Management")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for info message
        info_message = configured_page.get_by_text(re.compile(r"session", re.IGNORECASE))
        expect(info_message.first).to_be_visible()

    def test_status_indicators_present(self, configured_page: Page, streamlit_server: str):
        """Test that status indicators are displayed."""
        configured_page.goto(f"{streamlit_server}/API_Management")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for status indicators (success/error)
        # These may be displayed as success/error messages
        status_elements = configured_page.locator('[data-testid*="st"], .stAlert, .element-container')
        expect(status_elements.first).to_be_visible()

