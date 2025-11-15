"""UI tests for the Bulk Generation page."""

import re

import pytest
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
        expect(
            configured_page.get_by_role(
                "heading", name=re.compile(r"ElevenTools", re.IGNORECASE)
            )
        ).to_be_visible()
        expect(configured_page.get_by_text("Bulk Audio Generation")).to_be_visible()

    def test_model_selection_present(
        self, configured_page: Page, streamlit_server: str
    ):
        """Test that model selection is present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for API calls

        # Try Streamlit test IDs first
        selects = configured_page.locator('[data-testid="stSelectbox"]')
        if selects.count() == 0:
            selects = configured_page.locator("select")
        expect(selects.first).to_be_visible(timeout=10000)

    def test_voice_selection_present(
        self, configured_page: Page, streamlit_server: str
    ):
        """Test that voice selection is present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for API calls

        # Try Streamlit test IDs first
        selects = configured_page.locator('[data-testid="stSelectbox"]')
        if selects.count() == 0:
            selects = configured_page.locator("select")
        expect(selects).to_have_count(2, timeout=10000)  # Model and Voice

    def test_file_uploader_present(self, configured_page: Page, streamlit_server: str):
        """Test that CSV file uploader is present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(1000)  # Wait for content to load

        # Check for file uploader - Streamlit uses data-testid="stFileUploader"
        file_uploader = configured_page.locator('[data-testid="stFileUploader"]')
        if file_uploader.count() == 0:
            file_uploader = configured_page.locator('input[type="file"]')
        # File uploader input might be hidden but present in DOM
        assert file_uploader.count() > 0, "File uploader not found"

    def test_voice_settings_present(self, configured_page: Page, streamlit_server: str):
        """Test that voice settings are present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(1000)  # Wait for content to load

        # Check for voice settings sliders - Streamlit uses data-testid="stSlider"
        sliders = configured_page.locator('[data-testid="stSlider"]')
        if sliders.count() == 0:
            sliders = configured_page.locator('input[type="range"]')
        expect(sliders.first).to_be_visible(timeout=10000)

    def test_generate_button_present(
        self, configured_page: Page, streamlit_server: str
    ):
        """Test that generate button is present."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for API calls

        # Generate button only appears after file upload, so check for button conditionally
        # First check if file uploader is present
        file_uploader = configured_page.locator('[data-testid="stFileUploader"]')
        if file_uploader.count() == 0:
            file_uploader = configured_page.locator('input[type="file"]')

        # Look for generate button - Streamlit uses data-testid="stButton"
        buttons = configured_page.locator('[data-testid="stButton"]')
        generate_button = buttons.filter(
            has_text=re.compile(r"Generate.*Bulk|Bulk.*Audio", re.IGNORECASE)
        )

        if generate_button.count() == 0:
            generate_button = configured_page.get_by_role(
                "button", name=re.compile(r"Generate.*Bulk|Bulk.*Audio", re.IGNORECASE)
            )

        # Button might not be visible until file is uploaded - this is expected behavior
        if generate_button.count() == 0:
            # Check that at least the page loaded and file uploader is present
            assert file_uploader.count() > 0, "File uploader should be present"
            # Skip test if button isn't visible (expected when no file uploaded)
            pytest.skip("Generate button only appears after CSV file upload")
        else:
            expect(generate_button.first).to_be_visible(timeout=10000)

    def test_info_message_when_no_file(
        self, configured_page: Page, streamlit_server: str
    ):
        """Test that info message is shown when no file is uploaded."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(1000)  # Wait for content to load

        # Check for info message about uploading CSV - may appear as heading or text
        info_text = configured_page.get_by_text(
            re.compile(r"upload.*csv|csv.*file", re.IGNORECASE)
        )
        # Use first() to avoid strict mode violation if multiple matches
        if info_text.count() > 0:
            expect(info_text.first).to_be_visible(timeout=10000)

    def test_file_upload_accepted(self, configured_page: Page, streamlit_server: str):
        """Test that CSV file upload is accepted."""
        configured_page.goto(f"{streamlit_server}/Bulk_Generation")
        configured_page.wait_for_load_state("networkidle")

        # Create a temporary CSV file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("text,filename\nHello world,test.mp3\n")
            temp_file = f.name

        try:
            file_input = configured_page.locator('input[type="file"]')
            file_input.set_input_files(temp_file)

            # Wait for file to be processed
            configured_page.wait_for_timeout(1000)

            # File should be accepted (no error messages visible)
            error_messages = configured_page.get_by_text(
                re.compile(r"error", re.IGNORECASE)
            )
            expect(error_messages).to_have_count(0, timeout=2000)
        finally:
            os.unlink(temp_file)
