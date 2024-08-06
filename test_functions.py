import pytest
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO
import pandas as pd
from functions import (
    detect_string_variables,
    detect_phonetic_variables,
    detect_phonetic_conversion,
)
from Elevenlabs_functions import (
    fetch_models,
    fetch_voices,
    get_voice_id,
    generate_audio,
    process_text,
    bulk_generate_audio,
)
from ollama_functions import (
    enhance_script_with_ollama,
    convert_word_to_phonetic,
)

# Existing tests
def test_detect_string_variables():
    text = "Hello {name}, welcome to {place}!"
    result = detect_string_variables(text)
    assert result == ["name", "place"]

def test_detect_phonetic_variables():
    text = "The pronunciation of [[word]] is important."
    result = detect_phonetic_variables(text)
    assert result == ["word"]

def test_detect_phonetic_conversion():
    script = "Say [[english:hello]] and [[french:bonjour]]"
    result = detect_phonetic_conversion(script)
    assert result == [("english", "hello"), ("french", "bonjour")]

def test_detect_string_variables_no_variables():
    text = "Hello, welcome to our place!"
    result = detect_string_variables(text)
    assert result == []

def test_detect_phonetic_variables_no_variables():
    text = "The pronunciation is important."
    result = detect_phonetic_variables(text)
    assert result == []

def test_detect_phonetic_conversion_no_conversion():
    script = "Say hello and bonjour"
    result = detect_phonetic_conversion(script)
    assert result == []

# Tests for Elevenlabs functions
@pytest.fixture
def mock_requests():
    with patch('Elevenlabs_functions.requests.get') as mock_get:
        yield mock_get

def test_fetch_models(mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"model_id": "model1", "name": "Model 1"},
        {"model_id": "model2", "name": "Model 2"}
    ]
    mock_requests.return_value = mock_response

    result = fetch_models("fake_api_key")
    assert result == [("model1", "Model 1"), ("model2", "Model 2")]

def test_fetch_voices(mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "voices": [
            {"voice_id": "voice1", "name": "Voice 1"},
            {"voice_id": "voice2", "name": "Voice 2"}
        ]
    }
    mock_requests.return_value = mock_response

    result = fetch_voices("fake_api_key")
    assert result == [("voice1", "Voice 1"), ("voice2", "Voice 2")]

def test_get_voice_id():
    voices = [("voice1", "Voice 1"), ("voice2", "Voice 2")]
    assert get_voice_id(voices, "Voice 1") == "voice1"
    assert get_voice_id(voices, "Voice 2") == "voice2"
    assert get_voice_id(voices, "Voice 3") is None

@patch('Elevenlabs_functions.requests.post')
@patch('Elevenlabs_functions.open', new_callable=mock_open)
def test_generate_audio(mock_file, mock_post):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_response.headers = {"x-seed": "12345"}
    mock_post.return_value = mock_response

    success, seed = generate_audio(
        "fake_api_key",
        0.5,
        "model1",
        0.7,
        0.5,
        True,
        "voice1",
        "Hello, world!",
        "output.mp3"
    )

    assert success is True
    assert seed == "12345"
    mock_file.assert_called_once_with("output.mp3", "wb")
    mock_file().write.assert_called_once_with(b"fake audio content")

@patch('Elevenlabs_functions.requests.post')
def test_generate_audio_failure(mock_post):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.text = "API Error"
    mock_post.return_value = mock_response

    success, seed = generate_audio(
        "fake_api_key",
        0.5,
        "model1",
        0.7,
        0.5,
        True,
        "voice1",
        "Hello, world!",
        "output.mp3"
    )

    assert success is False
    assert seed is None

# New tests for process_text and bulk_generate_audio
def test_process_text():
    text = "Hello {name}\\nWelcome to {place}!"
    processed_text, variables = process_text(text)
    assert processed_text == "Hello {name}\nWelcome to {place}!"
    assert variables == ["name", "place"]

@patch('Elevenlabs_functions.generate_audio')
def test_bulk_generate_audio(mock_generate_audio):
    mock_generate_audio.return_value = (True, "12345")
    
    csv_content = "text,filename\nHello {name},greeting_{name}\nWelcome to {place},welcome_{place}"
    csv_file = StringIO(csv_content)
    
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "speaker_boost": True
    }
    
    result_df = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Fixed",
        seed="54321"
    )
    
    assert len(result_df) == 2
    assert result_df['filename'].tolist() == ['greeting_{name}.mp3', 'welcome_{place}.mp3']
    assert result_df['text'].tolist() == ['Hello {name}', 'Welcome to {place}']
    assert all(result_df['success'])
    assert all(result_df['seed'] == "12345")

@patch('Elevenlabs_functions.generate_audio')
def test_bulk_generate_audio_with_empty_csv(mock_generate_audio):
    csv_file = StringIO("")
    
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "speaker_boost": True
    }
    
    result_df = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Fixed",
        seed="54321"
    )
    
    assert result_df.empty

@patch('Elevenlabs_functions.generate_audio')
def test_bulk_generate_audio_with_random_seed(mock_generate_audio):
    mock_generate_audio.return_value = (True, None)
    
    csv_content = "text,filename\nHello {name},greeting_{name}"
    csv_file = StringIO(csv_content)
    
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "speaker_boost": True
    }
    
    result_df = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Random"
    )
    
    assert len(result_df) == 1
    assert result_df['filename'].tolist() == ['greeting_{name}.mp3']
    assert result_df['text'].tolist() == ['Hello {name}']
    assert all(result_df['success'])
    assert result_df['seed'].iloc[0] is not None  # Random seed should be generated

# New tests for ollama_functions
@patch('requests.post')
def test_enhance_script_with_ollama(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "I am so excited to share this incredible news with you! <break time=\"0.5s\"/> We have just made a groundbreaking discovery that will revolutionize the way we think about science and technology. <break time=\"0.3s\"/> This breakthrough has the potential to change lives and shape the future of our world. <break time=\"0.5s\"/> Stay tuned for more details as we unveil this amazing innovation!"
    }
    mock_post.return_value = mock_response

    script = "Original script content"
    enhancement_prompt = "Enhance this script"
    progress_callback = MagicMock()

    success, result = enhance_script_with_ollama(script, enhancement_prompt, progress_callback)

    assert success is True
    assert result.startswith("I am so excited to share this incredible news with you!")
    assert "<break time=" in result
    mock_post.assert_called_once()
    progress_callback.assert_called()

@patch('requests.post')
def test_convert_word_to_phonetic(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "/foʊˈnɛtɪk/"}
    mock_post.return_value = mock_response

    word = "phonetic"
    language = "english"
    model = "llama2"

    result = convert_word_to_phonetic(word, language, model)

    assert result == "/foʊˈnɛtɪk/"
    mock_post.assert_called_once()

@patch('requests.post')
def test_convert_word_to_phonetic_error(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "/ɪnˈvælɪd/"}
    mock_post.return_value = mock_response

    word = "invalidword"
    language = "unknown"
    model = "llama2"

    result = convert_word_to_phonetic(word, language, model)

    assert result == "/ɪnˈvælɪd/"
    mock_post.assert_called_once()
