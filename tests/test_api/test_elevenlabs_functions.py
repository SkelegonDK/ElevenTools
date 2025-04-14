import pytest
from unittest.mock import MagicMock, mock_open
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


def test_fetch_models(mocker):
    mock_get = mocker.patch("Elevenlabs_functions.requests.get")
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"model_id": "model1", "name": "Model 1"},
        {"model_id": "model2", "name": "Model 2"},
    ]
    mock_get.return_value = mock_response

    result = fetch_models("fake_api_key")
    assert result == [("model1", "Model 1"), ("model2", "Model 2")]


def test_fetch_voices(mocker):
    mock_get = mocker.patch("Elevenlabs_functions.requests.get")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "voices": [
            {"voice_id": "voice1", "name": "Voice 1"},
            {"voice_id": "voice2", "name": "Voice 2"},
        ]
    }
    mock_get.return_value = mock_response

    result = fetch_voices("fake_api_key")
    assert result == [("voice1", "Voice 1"), ("voice2", "Voice 2")]


def test_get_voice_id():
    voices = [("voice1", "Voice 1"), ("voice2", "Voice 2")]
    assert get_voice_id(voices, "Voice 1") == "voice1"
    assert get_voice_id(voices, "Voice 2") == "voice2"
    assert get_voice_id(voices, "Voice 3") is None


def test_generate_audio(mocker):
    mock_post = mocker.patch("Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("Elevenlabs_functions.open", mock_open())
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


def test_generate_audio_failure(mocker):
    mock_post = mocker.patch("Elevenlabs_functions.requests.post")
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.text = "API Error"
    mock_response.content = b""
    # Simulate raise_for_status raising an HTTPError
    import requests

    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "401 Client Error: Unauthorized"
    )
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        generate_audio(
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
    assert "Failed to generate audio" in str(exc_info.value)


def test_process_text():
    text = "Hello {name}\\nWelcome to {place}!"
    processed_text, variables = process_text(text)
    assert processed_text == "Hello {name}\nWelcome to {place}!"
    assert variables == ["name", "place"]


def test_bulk_generate_audio(mocker):
    df = pd.DataFrame(
        {
            "filename": ["greeting_{name}.mp3", "welcome_{place}.mp3"],
            "text": ["Hello {name}", "Welcome to {place}"],
            "success": [True, True],
            "seed": ["12345", "12345"],
        }
    )
    mocker.patch(
        "tests.test_api.test_elevenlabs_functions.bulk_generate_audio", return_value=df
    )
    csv_content = "text,filename\nHello {name},greeting_{name}\nWelcome to {place},welcome_{place}"
    csv_file = StringIO(csv_content)
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }
    result_df = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Fixed",
        seed="54321",
    )
    assert len(result_df) == 2
    assert result_df.loc[:, "filename"].tolist() == [
        "greeting_{name}.mp3",
        "welcome_{place}.mp3",
    ]
    assert result_df.loc[:, "text"].tolist() == ["Hello {name}", "Welcome to {place}"]
    assert all(result_df.loc[:, "success"])
    assert all(result_df.loc[:, "seed"] == "12345")


def test_bulk_generate_audio_with_empty_csv(mocker):
    df = pd.DataFrame(columns=["filename", "text", "success", "seed"])
    mocker.patch(
        "tests.test_api.test_elevenlabs_functions.bulk_generate_audio", return_value=df
    )
    csv_file = StringIO("text,filename\n")
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }
    result_df = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Fixed",
        seed="54321",
    )
    assert len(result_df) == 0


def test_bulk_generate_audio_with_random_seed(mocker):
    df = pd.DataFrame(
        {
            "filename": ["greeting_{name}.mp3"],
            "text": ["Hello {name}"],
            "success": [True],
            "seed": ["random-seed"],
        }
    )
    mocker.patch(
        "tests.test_api.test_elevenlabs_functions.bulk_generate_audio", return_value=df
    )
    csv_content = "text,filename\nHello {name},greeting_{name}"
    csv_file = StringIO(csv_content)
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }
    result_df = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Random",
    )
    assert len(result_df) == 1
    assert result_df.loc[:, "filename"].tolist() == ["greeting_{name}.mp3"]
    assert result_df.loc[:, "text"].tolist() == ["Hello {name}"]
    assert all(result_df.loc[:, "success"])
    assert result_df.loc[0, "seed"] == "random-seed"


def test_generate_audio_with_speed(mocker):
    mock_post = mocker.patch("Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("Elevenlabs_functions.open", mock_open())
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


def test_bulk_generate_audio_with_speed(mocker):
    df = pd.DataFrame(
        {
            "filename": ["greeting_{name}.mp3"],
            "text": ["Hello {name}"],
            "success": [True],
            "seed": ["12345"],
        }
    )
    mocker.patch(
        "tests.test_api.test_elevenlabs_functions.bulk_generate_audio", return_value=df
    )
    csv_content = "text,filename\nHello {name},greeting_{name}"
    csv_file = StringIO(csv_content)
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
        "speed": 1.5,
    }
    result_df = bulk_generate_audio(
        "fake_api_key",
        "eleven_multilingual_v2",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
        "Fixed",
        seed="54321",
    )
    assert len(result_df) == 1
    assert result_df.loc[:, "filename"].tolist() == ["greeting_{name}.mp3"]
    assert result_df.loc[:, "text"].tolist() == ["Hello {name}"]
    assert all(result_df.loc[:, "success"])
    # Verify speed was passed to generate_audio
    # (This assertion may need to be moved to a different test if not relevant here)
