import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Streamlit pages
from navigation.Home import *
from navigation.Bulk_Generation import *


@pytest.fixture
def mock_streamlit():
    with patch("streamlit.sidebar") as mock_sidebar, patch(
        "streamlit.title"
    ) as mock_title, patch("streamlit.subheader") as mock_subheader, patch(
        "streamlit.selectbox"
    ) as mock_selectbox, patch(
        "streamlit.text_area"
    ) as mock_text_area, patch(
        "streamlit.text_input"
    ) as mock_text_input, patch(
        "streamlit.button"
    ) as mock_button, patch(
        "streamlit.expander"
    ) as mock_expander, patch(
        "streamlit.slider"
    ) as mock_slider, patch(
        "streamlit.checkbox"
    ) as mock_checkbox, patch(
        "streamlit.file_uploader"
    ) as mock_file_uploader:
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
        }


@pytest.fixture
def mock_elevenlabs_functions():
    with patch("Elevenlabs_functions.fetch_models") as mock_fetch_models, patch(
        "Elevenlabs_functions.fetch_voices"
    ) as mock_fetch_voices, patch(
        "Elevenlabs_functions.generate_audio"
    ) as mock_generate_audio, patch(
        "Elevenlabs_functions.bulk_generate_audio"
    ) as mock_bulk_generate_audio:
        yield {
            "fetch_models": mock_fetch_models,
            "fetch_voices": mock_fetch_voices,
            "generate_audio": mock_generate_audio,
            "bulk_generate_audio": mock_bulk_generate_audio,
        }


@pytest.fixture
def mock_ollama_functions():
    with patch(
        "ollama_functions.enhance_script_with_ollama"
    ) as mock_enhance_script, patch(
        "ollama_functions.convert_word_to_phonetic"
    ) as mock_convert_word:
        yield {"enhance_script": mock_enhance_script, "convert_word": mock_convert_word}


def test_home_page(mock_streamlit, mock_elevenlabs_functions, mock_ollama_functions):
    # Set up mock returns
    mock_elevenlabs_functions["fetch_models"].return_value = [
        ("model1", "Model 1"),
        ("model2", "Model 2"),
    ]
    mock_elevenlabs_functions["fetch_voices"].return_value = [
        ("voice1", "Voice 1"),
        ("voice2", "Voice 2"),
    ]
    mock_elevenlabs_functions["generate_audio"].return_value = (True, "12345")
    mock_ollama_functions["enhance_script"].return_value = (True, "Enhanced script")
    mock_ollama_functions["convert_word"].return_value = "/foʊˈnɛtɪk/"

    # Set up session state
    if "generated_audio" not in st.session_state:
        st.session_state["generated_audio"] = []

    # Simulate user inputs
    mock_streamlit["selectbox"].side_effect = ["Model 1", "Voice 1"]
    mock_streamlit["text_area"].return_value = "Hello, world!"
    mock_streamlit["text_input"].return_value = "Enhance the script"
    mock_streamlit["button"].side_effect = [
        True,
        False,
    ]  # Enhance script, Generate audio
    mock_streamlit["slider"].side_effect = [0.5, 0.7, 0.3]
    mock_streamlit["checkbox"].return_value = True

    # Run the main function of the Home page
    # Note: This is a simplified version, as we can't actually run the Streamlit app in a test environment
    # Instead, we're checking if the key functions are called with the expected parameters

    # Check if models and voices are fetched
    assert mock_elevenlabs_functions["fetch_models"].called
    assert mock_elevenlabs_functions["fetch_voices"].called

    # Check if script enhancement is called
    assert mock_ollama_functions["enhance_script"].called
    mock_ollama_functions["enhance_script"].assert_called_with(
        "Hello, world!", "Enhance the script", pytest.approx
    )

    # Check if audio generation is called
    assert mock_elevenlabs_functions["generate_audio"].called
    mock_elevenlabs_functions["generate_audio"].assert_called_with(
        st.secrets["ELEVENLABS_API_KEY"],
        0.5,
        "model1",
        0.7,
        0.3,
        True,
        "voice1",
        "Enhanced script",
        pytest.approx,
        seed=None,
    )


def test_bulk_generation_page(mock_streamlit, mock_elevenlabs_functions):
    # Set up mock returns
    mock_elevenlabs_functions["fetch_models"].return_value = [
        ("model1", "Model 1"),
        ("model2", "Model 2"),
    ]
    mock_elevenlabs_functions["fetch_voices"].return_value = [
        ("voice1", "Voice 1"),
        ("voice2", "Voice 2"),
    ]
    mock_elevenlabs_functions["bulk_generate_audio"].return_value = pd.DataFrame(
        {
            "filename": ["audio1.mp3", "audio2.mp3"],
            "text": ["Hello, world!", "Goodbye, world!"],
            "success": [True, True],
            "seed": ["12345", "67890"],
        }
    )

    # Simulate user inputs
    mock_streamlit["selectbox"].side_effect = ["Model 1", "Voice 1"]
    mock_streamlit["slider"].side_effect = [0.5, 0.7, 0.3]
    mock_streamlit["checkbox"].return_value = True
    mock_streamlit["file_uploader"].return_value = MagicMock()
    mock_streamlit["button"].return_value = True  # Generate Bulk Audio

    # Run the main function of the Bulk Generation page
    # Note: This is a simplified version, as we can't actually run the Streamlit app in a test environment
    # Instead, we're checking if the key functions are called with the expected parameters

    # Check if models and voices are fetched
    assert mock_elevenlabs_functions["fetch_models"].called
    assert mock_elevenlabs_functions["fetch_voices"].called

    # Check if bulk audio generation is called
    assert mock_elevenlabs_functions["bulk_generate_audio"].called
    mock_elevenlabs_functions["bulk_generate_audio"].assert_called_with(
        st.secrets["ELEVENLABS_API_KEY"],
        "model1",
        "voice1",
        pytest.approx,
        pytest.approx,
        {
            "stability": 0.5,
            "similarity_boost": 0.7,
            "style": 0.3,
            "speaker_boost": True,
        },
        "Random",
        seed=None,
    )

    # Check if the results are displayed
    assert mock_streamlit["write"].called
