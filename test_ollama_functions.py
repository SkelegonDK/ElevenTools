import pytest
from unittest.mock import patch, MagicMock
from ollama_functions import enhance_script_with_ollama, convert_word_to_phonetic


@patch("subprocess.Popen")
def test_enhance_script_with_ollama(mock_popen):
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = ("Enhanced script content", "")
    mock_popen.return_value = mock_process

    script = "Original script content"
    enhancement_prompt = "Enhance this script"
    progress_callback = MagicMock()

    success, result = enhance_script_with_ollama(
        script, enhancement_prompt, progress_callback
    )

    assert success is True
    assert result == "Enhanced script content"
    mock_popen.assert_called_once()
    progress_callback.assert_called()


@patch("subprocess.Popen")
def test_enhance_script_with_ollama_failure(mock_popen):
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.communicate.return_value = ("", "Error occurred")
    mock_popen.return_value = mock_process

    script = "Original script content"
    enhancement_prompt = "Enhance this script"
    progress_callback = MagicMock()

    success, result = enhance_script_with_ollama(
        script, enhancement_prompt, progress_callback
    )

    assert success is False
    assert "Error occurred" in result
    mock_popen.assert_called_once()
    progress_callback.assert_called()


@patch("subprocess.Popen")
def test_convert_word_to_phonetic(mock_popen):
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = ("/foʊˈnɛtɪk/", "")
    mock_popen.return_value = mock_process

    word = "phonetic"
    language = "english"
    model = "eleven_monolingual_v1"

    result = convert_word_to_phonetic(word, language, model)

    assert result == "/foʊˈnɛtɪk/"
    mock_popen.assert_called_once()


@patch("subprocess.Popen")
def test_convert_word_to_phonetic_failure(mock_popen):
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.communicate.return_value = ("", "Error occurred")
    mock_popen.return_value = mock_process

    word = "invalidword"
    language = "unknown"
    model = "eleven_monolingual_v1"

    result = convert_word_to_phonetic(word, language, model)

    assert result is None
    mock_popen.assert_called_once()
