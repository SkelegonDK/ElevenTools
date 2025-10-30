"""UI tests for the Bulk Generation page."""

import pytest
import re
from playwright.sync_api import Page, expect


class TestBulkGenerationPage:
    """Test suite for the Bulk Generation page."""

    def test_page_loads(self, configured_page: Page, streamlit_server: str):
        """Test that the Bulk Generation page loads successfully."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check page title
        expect(configured_page).to_have_title("Bulk Generation")
        
        # Check main heading
        expect(configured_page.get_by_role("heading", name=re.compile(r'ElevenTools', re.IGNORECASE))).to_be_visible()
        expect(configured_page.get_by_text("Bulk Audio Generation")).to_be_visible()

    def test_model_selection_present(self, configured_page: Page, streamlit_server: str):
        """Test that model selection is present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        
        selects = configured_page.locator('select')
        expect(selects.first).to_be_visible()

    def test_voice_selection_present(self, configured_page: Page, streamlit_server: str):
        """Test that voice selection is present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        
        selects = configured_page.locator('select')
        expect(selects).to_have_count(2, timeout=10000)  # Model and Voice

    def test_file_uploader_present(self, configured_page: Page, streamlit_server: str):
        """Test that CSV file uploader is present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for file uploader
        file_uploader = configured_page.locator('input[type="file"]')
        expect(file_uploader).to_be_visible()

    def test_voice_settings_present(self, configured_page: Page, streamlit_server: str):
        """Test that voice settings are present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for voice settings sliders
        sliders = configured_page.locator('input[type="range"]')
        expect(sliders.first).to_be_visible()

    def test_generate_button_present(self, configured_page: Page, streamlit_server: str):
        """Test that generate button is present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        
        # Look for generate button
        generate_button = configured_page.get_by_role("button", name=re.compile(r'Generate', re.IGNORECASE))
        expect(generate_button).to_be_visible()

    def test_info_message_when_no_file(self, configured_page: Page, streamlit_server: str):
        """Test that info message is shown when no file is uploaded."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        
        # Check for info message about uploading CSV
        info_text = configured_page.get_by_text(re.compile(r"upload.*csv", re.IGNORECASE))
        expect(info_text).to_be_visible()

    def test_file_upload_accepted(self, configured_page: Page, streamlit_server: str):
        """Test that CSV file upload is accepted."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        
        # Create a temporary CSV file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("text,filename\nHello world,test.mp3\n")
            temp_file = f.name
        
        try:
            file_input = configured_page.locator('input[type="file"]')
            file_input.set_input_files(temp_file)
            
            # Wait for file to be processed
            configured_page.wait_for_timeout(1000)
            
            # File should be accepted (no error messages visible)
            error_messages = configured_page.get_by_text(re.compile(r"error", re.IGNORECASE))
            expect(error_messages).to_have_count(0, timeout=2000)
        finally:
            os.unlink(temp_file)

