"""UI tests for the main Streamlit app page."""

import pytest
import re
from playwright.sync_api import Page, expect


class TestMainPage:
    """Test suite for the main app.py page."""

    def test_page_loads(self, configured_page: Page, streamlit_server: str):
        """Test that the main page loads successfully."""
        configured_page.goto(streamlit_server)
        
        # Check page title
        expect(configured_page).to_have_title("ElevenTools")
        
        # Check main heading
        expect(configured_page.get_by_role("heading", name="ElevenTools")).to_be_visible()
        expect(configured_page.get_by_text("Advanced Text-to-Speech")).to_be_visible()

    def test_model_selection_present(self, configured_page: Page, streamlit_server: str):
        """Test that model selection dropdown is present."""
        configured_page.goto(streamlit_server)
        
        # Wait for page to load
        configured_page.wait_for_load_state("networkidle")
        
        # Check for model selectbox (Streamlit renders as select)
        model_select = configured_page.locator('select').first
        expect(model_select).to_be_visible()

    def test_voice_selection_present(self, configured_page: Page, streamlit_server: str):
        """Test that voice selection dropdown is present."""
        configured_page.goto(streamlit_server)
        
        # Wait for page to load
        configured_page.wait_for_load_state("networkidle")
        
        # Check for voice selectbox (Streamlit renders as select)
        selects = configured_page.locator('select')
        expect(selects).to_have_count(2, timeout=10000)  # Model and Voice

    def test_text_area_present(self, configured_page: Page, streamlit_server: str):
        """Test that text input area is present."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        
        # Check for text area
        text_area = configured_page.locator('textarea').first
        expect(text_area).to_be_visible()

    def test_voice_settings_expander(self, configured_page: Page, streamlit_server: str):
        """Test that voice settings expander is present."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        
        # Look for voice settings label or slider
        # Streamlit renders sliders with specific structure
        sliders = configured_page.locator('input[type="range"]')
        expect(sliders.first).to_be_visible(timeout=10000)  # At least one slider should be visible

    def test_generate_button_present(self, configured_page: Page, streamlit_server: str):
        """Test that generate audio button is present."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        
        # Check for button with "Generate Audio" text
        generate_button = configured_page.get_by_role("button", name=re.compile(r'Generate Audio', re.IGNORECASE))
        expect(generate_button).to_be_visible()

    def test_text_input_functionality(self, configured_page: Page, streamlit_server: str):
        """Test that text can be entered in the text area."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        
        text_area = configured_page.locator('textarea').first
        test_text = "Hello, this is a test message."
        
        text_area.fill(test_text)
        expect(text_area).to_have_value(test_text)

    def test_variable_detection_display(self, configured_page: Page, streamlit_server: str):
        """Test that variables in text are detected and displayed."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        
        text_area = configured_page.locator('textarea').first
        text_with_variables = "Hello {name}, welcome to {place}!"
        
        text_area.fill(text_with_variables)
        
        # Wait for variable detection (if implemented)
        # This test may need adjustment based on actual UI implementation
        configured_page.wait_for_timeout(500)  # Give time for processing
        
        # Check if variables are displayed (implementation-dependent)
        # This is a placeholder - adjust based on actual UI

    def test_sidebar_navigation(self, configured_page: Page, streamlit_server: str):
        """Test that sidebar navigation is accessible."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        
        # Check for sidebar navigation links
        # Streamlit renders navigation in sidebar
        sidebar = configured_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

    def test_page_responsive(self, configured_page: Page, streamlit_server: str):
        """Test that page is responsive."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        
        # Test mobile viewport
        configured_page.set_viewport_size({"width": 375, "height": 667})
        expect(configured_page.get_by_role("heading", name="ElevenTools")).to_be_visible()
        
        # Test tablet viewport
        configured_page.set_viewport_size({"width": 768, "height": 1024})
        expect(configured_page.get_by_role("heading", name="ElevenTools")).to_be_visible()
        
        # Test desktop viewport
        configured_page.set_viewport_size({"width": 1920, "height": 1080})
        expect(configured_page.get_by_role("heading", name="ElevenTools")).to_be_visible()

