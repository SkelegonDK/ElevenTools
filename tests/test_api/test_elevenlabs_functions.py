import pytest
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO
import pandas as pd
from typing import cast
from pandas import DataFrame
from Elevenlabs_functions import (
    fetch_models,
    fetch_voices,
    get_voice_id,
    generate_audio,
    process_text,
    bulk_generate_audio,
    ValidationError,
)


@pytest.fixture
def mock_requests():
    with patch("Elevenlabs_functions.requests.get") as mock_get:
        yield mock_get


def test_fetch_models(mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"model_id": "model1", "name": "Model 1"},
        {"model_id": "model2", "name": "Model 2"},
    ]
    mock_requests.return_value = mock_response

    result = fetch_models("fake_api_key")
    assert result == [("model1", "Model 1"), ("model2", "Model 2")]


def test_fetch_voices(mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "voices": [
            {"voice_id": "voice1", "name": "Voice 1"},
            {"voice_id": "voice2", "name": "Voice 2"},
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


@patch("Elevenlabs_functions.requests.post")
@patch("Elevenlabs_functions.open", new_callable=mock_open)
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
        "output.mp3",
    )

    assert success is True
    assert seed == "12345"
    mock_file.assert_called_once_with("output.mp3", "wb")
    mock_file().write.assert_called_once_with(b"fake audio content")


@patch("Elevenlabs_functions.requests.post")
def test_generate_audio_failure(mock_post):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.text = "API Error"
    mock_response.content = b""
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
        "output.mp3",
    )

    assert success is False
    assert seed is None


def test_process_text():
    text = "Hello {name}\\nWelcome to {place}!"
    processed_text, variables = process_text(text)
    assert processed_text == "Hello {name}\nWelcome to {place}!"
    assert variables == ["name", "place"]


@patch("Elevenlabs_functions.generate_audio")
def test_bulk_generate_audio(mock_generate_audio):
    mock_generate_audio.return_value = (True, "12345")

    csv_content = "text,filename\nHello {name},greeting_{name}\nWelcome to {place},welcome_{place}"
    csv_file = StringIO(csv_content)

    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }

    result = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Fixed",
        seed="54321",
    )

    result_df = cast(DataFrame, result)
    assert len(result_df) == 2
    assert result_df.loc[:, "filename"].tolist() == [
        "greeting_{name}.mp3",
        "welcome_{place}.mp3",
    ]
    assert result_df.loc[:, "text"].tolist() == ["Hello {name}", "Welcome to {place}"]
    assert all(result_df.loc[:, "success"])
    assert all(result_df.loc[:, "seed"] == "12345")


@patch("Elevenlabs_functions.generate_audio")
def test_bulk_generate_audio_with_empty_csv(mock_generate_audio):
    csv_file = StringIO("text,filename\n")

    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }

    result = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Fixed",
        seed="54321",
    )

    result_df = cast(DataFrame, result)
    assert len(result_df) == 0


@patch("Elevenlabs_functions.generate_audio")
def test_bulk_generate_audio_with_random_seed(mock_generate_audio):
    mock_generate_audio.return_value = (True, None)

    csv_content = "text,filename\nHello {name},greeting_{name}"
    csv_file = StringIO(csv_content)

    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }

    result = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Random",
    )

    result_df = cast(DataFrame, result)
    assert len(result_df) == 1
    assert result_df.loc[:, "filename"].tolist() == ["greeting_{name}.mp3"]
    assert result_df.loc[:, "text"].tolist() == ["Hello {name}"]
    assert all(result_df.loc[:, "success"])
    assert result_df.loc[0, "seed"] is not None


@patch("Elevenlabs_functions.requests.post")
@patch("Elevenlabs_functions.open", new_callable=mock_open)
def test_generate_audio_with_speed(mock_file, mock_post):
    """Test generate_audio with speed parameter for multilingual v2 model."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_response.headers = {"x-seed": "12345"}
    mock_post.return_value = mock_response

    # Test valid speed with multilingual v2 model
    success, seed = generate_audio(
        "fake_api_key",
        0.5,
        "eleven_multilingual_v2",
        0.7,
        0.5,
        True,
        "voice1",
        "Hello, world!",
        "output.mp3",
        speed=1.5,
    )

    assert success is True
    assert seed == "12345"

    # Verify speed was included in payload
    payload = mock_post.call_args[1]["json"]
    assert payload["voice_settings"]["speed"] == 1.5


def test_generate_audio_speed_validation():
    """Test speed parameter validation."""
    # Test speed with non-multilingual model
    with pytest.raises(
        ValidationError,
        match="Speed parameter is only supported for multilingual v2 model",
    ):
        generate_audio(
            "fake_api_key",
            0.5,
            "eleven_monolingual_v1",
            0.7,
            0.5,
            True,
            "voice1",
            "Hello, world!",
            "output.mp3",
            speed=1.5,
        )

    # Test speed out of range (too low)
    with pytest.raises(ValidationError, match="Speed must be between 0.5 and 2.0"):
        generate_audio(
            "fake_api_key",
            0.5,
            "eleven_multilingual_v2",
            0.7,
            0.5,
            True,
            "voice1",
            "Hello, world!",
            "output.mp3",
            speed=0.4,
        )

    # Test speed out of range (too high)
    with pytest.raises(ValidationError, match="Speed must be between 0.5 and 2.0"):
        generate_audio(
            "fake_api_key",
            0.5,
            "eleven_multilingual_v2",
            0.7,
            0.5,
            True,
            "voice1",
            "Hello, world!",
            "output.mp3",
            speed=2.1,
        )


@patch("Elevenlabs_functions.generate_audio")
def test_bulk_generate_audio_with_speed(mock_generate_audio):
    """Test bulk generation with speed parameter."""
    mock_generate_audio.return_value = (True, "12345")

    csv_content = "text,filename\nHello {name},greeting_{name}"
    csv_file = StringIO(csv_content)

    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
        "speed": 1.5,
    }

    result = bulk_generate_audio(
        "fake_api_key",
        "eleven_multilingual_v2",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Fixed",
        seed="54321",
    )

    result_df = cast(DataFrame, result)
    assert len(result_df) == 1
    assert result_df.loc[:, "filename"].tolist() == ["greeting_{name}.mp3"]
    assert result_df.loc[:, "text"].tolist() == ["Hello {name}"]
    assert all(result_df.loc[:, "success"])

    # Verify speed was passed to generate_audio
    call_kwargs = mock_generate_audio.call_args[1]
    assert call_kwargs.get("speed") == 1.5
