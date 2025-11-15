from io import StringIO
from unittest.mock import MagicMock, mock_open

import pandas as pd
import pytest

from scripts.Elevenlabs_functions import (
    ValidationError,
    bulk_generate_audio,
    fetch_models,
    fetch_voices,
    generate_audio,
    get_voice_id,
    process_text,
)


def test_fetch_models(mocker):
    mock_get = mocker.patch("scripts.Elevenlabs_functions.requests.get")
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"model_id": "model1", "name": "Model 1"},
        {"model_id": "model2", "name": "Model 2"},
    ]
    mock_get.return_value = mock_response

    result = fetch_models("fake_api_key")
    assert result == [("model1", "Model 1"), ("model2", "Model 2")]


def test_fetch_voices(mocker):
    mock_get = mocker.patch("scripts.Elevenlabs_functions.requests.get")
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
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_post.return_value = mock_response

    success = generate_audio(
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
    mock_file.assert_called_once_with("output.mp3", "wb")
    mock_file().write.assert_called_once_with(b"fake audio content")


def test_generate_audio_failure(mocker):
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
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
    )
    assert len(result_df) == 2
    assert result_df["filename"].tolist() == [
        "greeting_{name}.mp3",
        "welcome_{place}.mp3",
    ]
    assert result_df["text"].tolist() == ["Hello {name}", "Welcome to {place}"]
    assert all(result_df["success"].tolist())


def test_bulk_generate_audio_with_empty_csv(mocker):
    df = pd.DataFrame(columns=["filename", "text", "success"])
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
    )
    assert len(result_df) == 0


def test_bulk_generate_audio_with_random_seed(mocker):
    # Mock the HTTP request to generate_audio
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_audio_content"
    mock_post.return_value = mock_response

    # Mock file operations
    mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mocker.patch("os.makedirs")

    csv_content = "text,filename\nHello {name},greeting_{name}"
    csv_file = StringIO(csv_content)
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }
    success, message = bulk_generate_audio(
        "fake_api_key",
        "model1",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
    )
    assert success is True
    assert "completed successfully" in message
    assert mock_post.called


def test_generate_audio_with_speed(mocker):
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_post.return_value = mock_response
    # Test valid speed with multilingual v2 model
    success = generate_audio(
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
    # Verify speed was included in payload
    payload = mock_post.call_args[1]["json"]
    assert payload["voice_settings"]["speed"] == 1.5


def test_generate_audio_speed_validation():
    """Test speed parameter validation."""
    # Test speed with non-multilingual model
    with pytest.raises(
        ValidationError,
        match="Speed parameter is not supported for model",
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
    )
    assert len(result_df) == 1
    assert result_df.loc[:, "filename"].tolist() == ["greeting_{name}.mp3"]
    assert result_df.loc[:, "text"].tolist() == ["Hello {name}"]
    assert all(result_df.loc[:, "success"])
    # Verify speed was passed to generate_audio
    # (This assertion may need to be moved to a different test if not relevant here)


# Model-Voice Setting Compatibility Tests


def test_speed_validation_for_monolingual_v1():
    """Test that speed parameter raises ValidationError for eleven_monolingual_v1."""
    with pytest.raises(
        ValidationError,
        match="Speed parameter is not supported for model",
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


def test_speed_validation_for_other_models():
    """Test that speed parameter raises ValidationError for other non-multilingual models."""
    # Test with eleven_monolingual_v1 (doesn't match patterns)
    with pytest.raises(
        ValidationError,
        match="Speed parameter is not supported for model",
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

    # Test with a model that doesn't match any patterns (eleven_english_sts_v2 doesn't match patterns)
    with pytest.raises(
        ValidationError,
        match="Speed parameter is not supported for model",
    ):
        generate_audio(
            "fake_api_key",
            0.5,
            "eleven_english_sts_v2",
            0.7,
            0.5,
            True,
            "voice1",
            "Hello, world!",
            "output.mp3",
            speed=1.5,
        )


def test_multilingual_v2_speed_inclusion(mocker):
    """Test that speed is included in payload for eleven_multilingual_v2 when provided."""
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_post.return_value = mock_response

    success = generate_audio(
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
    # Verify speed was included in payload
    payload = mock_post.call_args[1]["json"]
    assert "voice_settings" in payload
    assert "speed" in payload["voice_settings"]
    assert payload["voice_settings"]["speed"] == 1.5
    assert isinstance(payload["voice_settings"]["speed"], float)


def test_multilingual_v2_speed_exclusion(mocker):
    """Test that speed is excluded from payload for eleven_multilingual_v2 when not provided."""
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_post.return_value = mock_response

    success = generate_audio(
        "fake_api_key",
        0.5,
        "eleven_multilingual_v2",
        0.7,
        0.5,
        True,
        "voice1",
        "Hello, world!",
        "output.mp3",
        speed=None,
    )

    assert success is True
    # Verify speed was NOT included in payload
    payload = mock_post.call_args[1]["json"]
    assert "voice_settings" in payload
    assert "speed" not in payload["voice_settings"]
    # Verify other settings are still present
    assert "stability" in payload["voice_settings"]
    assert "similarity_boost" in payload["voice_settings"]
    assert "style" in payload["voice_settings"]
    assert "use_speaker_boost" in payload["voice_settings"]


def test_monolingual_v1_no_speed_in_payload(mocker):
    """Test that speed is never included in payload for monolingual v1 even if validation passes somehow."""
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_post.return_value = mock_response

    # This should pass validation since speed=None
    success = generate_audio(
        "fake_api_key",
        0.5,
        "eleven_monolingual_v1",
        0.7,
        0.5,
        True,
        "voice1",
        "Hello, world!",
        "output.mp3",
        speed=None,
    )

    assert success is True
    # Verify speed was NOT included in payload
    payload = mock_post.call_args[1]["json"]
    assert "voice_settings" in payload
    assert "speed" not in payload["voice_settings"]


def test_common_settings_all_models(mocker):
    """Test that common voice settings work with all models."""
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_post.return_value = mock_response

    models_to_test = ["eleven_monolingual_v1", "eleven_multilingual_v2"]

    for model_id in models_to_test:
        # Reset mock to capture each call separately
        mock_post.reset_mock()

        success = generate_audio(
            "fake_api_key",
            0.5,  # stability
            model_id,
            0.7,  # similarity_boost
            0.3,  # style
            True,  # use_speaker_boost
            "voice1",
            "Hello, world!",
            "output.mp3",
        )

        assert success is True
        # Verify all common settings are in payload
        payload = mock_post.call_args[1]["json"]
        assert "voice_settings" in payload
        assert "stability" in payload["voice_settings"]
        assert payload["voice_settings"]["stability"] == 0.5
        assert isinstance(payload["voice_settings"]["stability"], float)

        assert "similarity_boost" in payload["voice_settings"]
        assert payload["voice_settings"]["similarity_boost"] == 0.7
        assert isinstance(payload["voice_settings"]["similarity_boost"], float)

        assert "style" in payload["voice_settings"]
        assert payload["voice_settings"]["style"] == 0.3
        assert isinstance(payload["voice_settings"]["style"], float)

        assert "use_speaker_boost" in payload["voice_settings"]
        assert payload["voice_settings"]["use_speaker_boost"] is True
        assert isinstance(payload["voice_settings"]["use_speaker_boost"], bool)

        # Verify model_id is correct
        assert payload["model_id"] == model_id


def test_payload_structure_per_model(mocker):
    """Test that payload structure is correct for different model types."""
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"fake audio content"
    mock_post.return_value = mock_response

    # Test monolingual v1 - should not have speed
    generate_audio(
        "fake_api_key",
        0.5,
        "eleven_monolingual_v1",
        0.7,
        0.5,
        True,
        "voice1",
        "Test text",
        "output.mp3",
    )
    payload = mock_post.call_args[1]["json"]
    assert "text" in payload
    assert "model_id" in payload
    assert payload["model_id"] == "eleven_monolingual_v1"
    assert "voice_settings" in payload
    assert "speed" not in payload["voice_settings"]
    assert (
        len(payload["voice_settings"]) == 4
    )  # stability, similarity_boost, style, use_speaker_boost

    # Reset mock
    mock_post.reset_mock()

    # Test multilingual v2 with speed - should have speed
    generate_audio(
        "fake_api_key",
        0.5,
        "eleven_multilingual_v2",
        0.7,
        0.5,
        True,
        "voice1",
        "Test text",
        "output.mp3",
        speed=1.2,
    )
    payload = mock_post.call_args[1]["json"]
    assert "text" in payload
    assert "model_id" in payload
    assert payload["model_id"] == "eleven_multilingual_v2"
    assert "voice_settings" in payload
    assert "speed" in payload["voice_settings"]
    assert payload["voice_settings"]["speed"] == 1.2
    assert len(payload["voice_settings"]) == 5  # + speed

    # Reset mock
    mock_post.reset_mock()

    # Test multilingual v2 without speed - should not have speed
    generate_audio(
        "fake_api_key",
        0.5,
        "eleven_multilingual_v2",
        0.7,
        0.5,
        True,
        "voice1",
        "Test text",
        "output.mp3",
        speed=None,
    )
    payload = mock_post.call_args[1]["json"]
    assert "text" in payload
    assert "model_id" in payload
    assert payload["model_id"] == "eleven_multilingual_v2"
    assert "voice_settings" in payload
    assert "speed" not in payload["voice_settings"]
    assert len(payload["voice_settings"]) == 4


def test_bulk_generation_model_compatibility(mocker):
    """Test that bulk generation respects model-voice setting compatibility."""
    mock_post = mocker.patch("scripts.Elevenlabs_functions.requests.post")
    mock_file = mocker.patch("scripts.Elevenlabs_functions.open", mock_open())
    mocker.patch("os.makedirs")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_audio_content"
    mock_post.return_value = mock_response

    csv_content = "text,filename\nHello {name},greeting_{name}"
    csv_file = StringIO(csv_content)

    # Test bulk generation with speed for multilingual v2 - should work
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
        "speed": 1.5,
    }
    success, message = bulk_generate_audio(
        "fake_api_key",
        "eleven_multilingual_v2",
        "voice1",
        csv_file,
        "output_dir",
        voice_settings,
    )
    assert success is True
    assert "completed successfully" in message
    # Verify speed was passed to generate_audio
    payload = mock_post.call_args[1]["json"]
    assert payload["voice_settings"]["speed"] == 1.5

    # Reset for next test
    mock_post.reset_mock()
    csv_file.seek(0)

    # Test bulk generation with speed for monolingual v1 - should raise APIError wrapping ValidationError
    from utils.error_handling import APIError

    with pytest.raises(APIError) as exc_info:
        bulk_generate_audio(
            "fake_api_key",
            "eleven_monolingual_v1",
            "voice1",
            csv_file,
            "output_dir",
            voice_settings,  # Contains speed
        )
    # Verify the error message contains the validation error
    assert "Speed parameter is not supported for model" in str(exc_info.value)
