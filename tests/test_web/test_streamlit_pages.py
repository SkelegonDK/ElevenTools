import os
import sys
from unittest.mock import patch

import pytest

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Streamlit pages
from pages.Bulk_Generation import *


@pytest.fixture(autouse=True)
def disable_streamlit_cache():
    """Disable Streamlit caching to avoid pickling issues with mocks."""

    def no_op_decorator(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    # Patch both streamlit.cache_data and utils.caching.st_cache
    with (
        patch("streamlit.cache_data", side_effect=no_op_decorator),
        patch("utils.caching.st_cache", side_effect=no_op_decorator),
    ):
        yield


@pytest.fixture
def mock_streamlit():
    with (
        patch("streamlit.sidebar") as mock_sidebar,
        patch("streamlit.title") as mock_title,
        patch("streamlit.subheader") as mock_subheader,
        patch("streamlit.selectbox") as mock_selectbox,
        patch("streamlit.text_area") as mock_text_area,
        patch("streamlit.text_input") as mock_text_input,
        patch("streamlit.button") as mock_button,
        patch("streamlit.expander") as mock_expander,
        patch("streamlit.slider") as mock_slider,
        patch("streamlit.checkbox") as mock_checkbox,
        patch("streamlit.file_uploader") as mock_file_uploader,
        patch("streamlit.write") as mock_write,
    ):
        yield {
            "sidebar": mock_sidebar,
            "title": mock_title,
            "subheader": mock_subheader,
            "selectbox": mock_selectbox,
            "text_area": mock_text_area,
            "text_input": mock_text_input,
            "button": mock_button,
            "expander": mock_expander,
            "slider": mock_slider,
            "checkbox": mock_checkbox,
            "file_uploader": mock_file_uploader,
            "write": mock_write,
        }


@pytest.fixture
def mock_elevenlabs_functions():
    with (
        patch("pages.Bulk_Generation.fetch_models") as mock_fetch_models,
        patch("scripts.Elevenlabs_functions.fetch_voices") as mock_fetch_voices,
        patch("scripts.Elevenlabs_functions.generate_audio") as mock_generate_audio,
        patch(
            "scripts.Elevenlabs_functions.bulk_generate_audio"
        ) as mock_bulk_generate_audio,
        patch(
            "streamlit.secrets",
            {"ELEVENLABS_API_KEY": "test_key", "OPENROUTER_API_KEY": "test_key"},
        ),
        patch("streamlit.session_state", {}),
    ):
        yield {
            "fetch_models": mock_fetch_models,
            "fetch_voices": mock_fetch_voices,
            "generate_audio": mock_generate_audio,
            "bulk_generate_audio": mock_bulk_generate_audio,
        }


@pytest.fixture
def mock_openrouter_functions():
    with (
        patch(
            "scripts.openrouter_functions.enhance_script_with_openrouter"
        ) as mock_enhance_script,
        patch(
            "scripts.openrouter_functions.convert_word_to_phonetic_openrouter"
        ) as mock_convert_word,
    ):
        yield {"enhance_script": mock_enhance_script, "convert_word": mock_convert_word}


@pytest.mark.skip(
    reason="Requires full Streamlit runtime context - use UI tests instead"
)
def test_home_page(
    mock_streamlit, mock_elevenlabs_functions, mock_openrouter_functions
):
    # Note: Testing full Streamlit pages requires Streamlit runtime context
    # This test is skipped in favor of UI tests with Playwright
    pass


@pytest.mark.skip(
    reason="Requires full Streamlit runtime context - use UI tests instead"
)
def test_bulk_generation_page(mock_streamlit, mock_elevenlabs_functions):
    # Note: Testing full Streamlit pages requires Streamlit runtime context
    # This test is skipped in favor of UI tests with Playwright
    pass
