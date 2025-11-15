import base64
import io
from typing import Any

import pandas as pd
import pytest

from scripts.Elevenlabs_functions import (
    bulk_generate_audio,
    create_voice_from_preview,
    generate_audio,
    generate_voice_previews,
)
from utils.error_handling import APIError, ValidationError


@pytest.mark.core_suite
def test_generate_audio_success(mocker, tmp_path):
    mock_response = mocker.Mock()
    mock_response.content = b"fake-bytes"
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch(
        "scripts.Elevenlabs_functions.requests.post",
        return_value=mock_response,
    )
    mocker.patch(
        "scripts.Elevenlabs_functions.supports_speed",
        return_value=True,
    )

    output_path = tmp_path / "output.mp3"

    result = generate_audio(
        "sk-test",
        stability=0.5,
        model_id="eleven_multilingual_v2",
        similarity_boost=0.6,
        style=0.4,
        use_speaker_boost=True,
        voice_id="voice_123",
        text_to_speak="Hello world",
        output_path=str(output_path),
        speed=1.1,
    )

    assert result is True
    assert output_path.read_bytes() == b"fake-bytes"


@pytest.mark.core_suite
def test_generate_audio_validation_errors():
    with pytest.raises(ValidationError):
        generate_audio(
            "sk-test",
            stability=-0.1,
            model_id="eleven_multilingual_v2",
            similarity_boost=0.5,
            style=0.3,
            use_speaker_boost=False,
            voice_id="voice_123",
            text_to_speak="Hello world",
        )

    with pytest.raises(ValidationError):
        generate_audio(
            "sk-test",
            stability=0.5,
            model_id="eleven_monolingual_v1",
            similarity_boost=0.5,
            style=0.3,
            use_speaker_boost=False,
            voice_id="voice_123",
            text_to_speak="Hello world",
            speed=1.2,
        )


@pytest.mark.core_suite
def test_generate_audio_api_error(mocker):
    from requests import exceptions as requests_exceptions

    mocker.patch(
        "scripts.Elevenlabs_functions.requests.post",
        side_effect=requests_exceptions.HTTPError("429"),
    )

    with pytest.raises(APIError):
        generate_audio(
            "sk-test",
            stability=0.5,
            model_id="eleven_multilingual_v2",
            similarity_boost=0.6,
            style=0.4,
            use_speaker_boost=True,
            voice_id="voice_123",
            text_to_speak="Hello world",
        )


@pytest.mark.core_suite
def test_generate_voice_previews_success(mocker, tmp_path, monkeypatch):
    fake_preview = {
        "generated_voice_id": "voice_generated",
        "audio_base_64": base64.b64encode(b"preview-bytes").decode("utf-8"),
    }
    mock_response = mocker.Mock()
    mock_response.raise_for_status = mocker.Mock()
    mock_response.json.return_value = {"previews": [fake_preview]}

    mocker.patch(
        "scripts.Elevenlabs_functions.requests.post",
        return_value=mock_response,
    )

    # Ensure previews are written inside tmp_path
    monkeypatch.chdir(tmp_path)

    result = generate_voice_previews("sk-test", "Warm narrator voice")

    assert result is not None
    assert result["generated_voice_id"] == "voice_generated"
    assert len(result["audio"]) == 1
    assert (tmp_path / "preview_0.mp3").read_bytes() == b"preview-bytes"


@pytest.mark.core_suite
def test_generate_voice_previews_validation_error():
    with pytest.raises(ValidationError):
        generate_voice_previews("sk-test", "")


@pytest.mark.core_suite
def test_create_voice_from_preview_success(mocker):
    mock_response = mocker.Mock()
    mock_response.raise_for_status = mocker.Mock()
    mock_response.json.return_value = {"status": "queued"}
    mocker.patch(
        "scripts.Elevenlabs_functions.requests.post",
        return_value=mock_response,
    )

    result = create_voice_from_preview(
        "sk-test",
        voice_name="Launch Voice",
        voice_description="Confident and upbeat",
        generated_voice_id="voice_generated",
    )

    assert result == {"status": "queued"}


@pytest.mark.core_suite
def test_create_voice_from_preview_validation_error():
    with pytest.raises(ValidationError):
        create_voice_from_preview(
            "sk-test",
            voice_name="",
            voice_description="Confident and upbeat",
            generated_voice_id="voice_generated",
        )


@pytest.mark.core_suite
def test_bulk_generate_audio_success(mocker, tmp_path, monkeypatch):
    # Arrange
    csv_content = (
        "text,filename\nHello {name},greeting_{name}\nWorld {name},world_{name}"
    )
    csv_file = io.BytesIO(csv_content.encode("utf-8"))

    def fake_generate_audio(_api_key: str, *_args: Any, **_kwargs: Any) -> bool:
        return True

    mocker.patch(
        "scripts.Elevenlabs_functions.generate_audio",
        side_effect=fake_generate_audio,
    )
    mocker.patch(
        "scripts.Elevenlabs_functions.validate_path_within_base",
        return_value=True,
    )
    mocker.patch(
        "scripts.Elevenlabs_functions.sanitize_filename",
        side_effect=lambda value: value + ".mp3",
    )

    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    monkeypatch.chdir(tmp_path)

    df_success = pd.DataFrame(
        [
            {"text": "Hello {name}", "filename": "greeting_{name}", "name": "Alice"},
            {"text": "World {name}", "filename": "world_{name}", "name": "Bob"},
        ]
    )
    mocker.patch("pandas.read_csv", return_value=df_success)

    success, message = bulk_generate_audio(
        api_key="sk-test",
        model_id="eleven_multilingual_v2",
        voice_id="voice_123",
        csv_file=csv_file,
        output_dir=str(outputs_dir),
        voice_settings={
            "stability": 0.5,
            "similarity_boost": 0.6,
            "style": 0.2,
            "use_speaker_boost": True,
        },
    )

    assert success is True
    assert "completed" in message.lower()


@pytest.mark.core_suite
def test_bulk_generate_audio_missing_columns(mocker, tmp_path, monkeypatch):
    # Arrange
    mocker.patch(
        "scripts.Elevenlabs_functions.validate_path_within_base",
        return_value=True,
    )

    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    monkeypatch.chdir(tmp_path)

    df_invalid = pd.DataFrame([{"name": "Alice"}])
    mocker.patch("pandas.read_csv", return_value=df_invalid)

    invalid_csv = io.BytesIO(b"name\nAlice")
    with pytest.raises(APIError):
        bulk_generate_audio(
            api_key="sk-test",
            model_id="eleven_multilingual_v2",
            voice_id="voice_123",
            csv_file=invalid_csv,
            output_dir=str(outputs_dir),
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.6,
                "style": 0.2,
                "use_speaker_boost": True,
            },
        )


@pytest.mark.core_suite
def test_bulk_generate_audio_downstream_error(mocker, tmp_path, monkeypatch):
    # Arrange
    csv_content = (
        "text,filename\nHello {name},greeting_{name}\nWorld {name},world_{name}"
    )
    csv_file_error = io.BytesIO(csv_content.encode("utf-8"))

    mocker.patch(
        "scripts.Elevenlabs_functions.generate_audio",
        side_effect=APIError("Failed", "Disk full"),
    )
    mocker.patch(
        "scripts.Elevenlabs_functions.validate_path_within_base",
        return_value=True,
    )
    mocker.patch(
        "scripts.Elevenlabs_functions.sanitize_filename",
        side_effect=lambda value: value + ".mp3",
    )

    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    monkeypatch.chdir(tmp_path)

    df_success = pd.DataFrame(
        [
            {"text": "Hello {name}", "filename": "greeting_{name}", "name": "Alice"},
            {"text": "World {name}", "filename": "world_{name}", "name": "Bob"},
        ]
    )
    mocker.patch("pandas.read_csv", return_value=df_success)

    with pytest.raises(APIError) as exc:
        bulk_generate_audio(
            api_key="sk-test",
            model_id="eleven_multilingual_v2",
            voice_id="voice_123",
            csv_file=csv_file_error,
            output_dir=str(outputs_dir),
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.6,
                "style": 0.2,
                "use_speaker_boost": True,
            },
        )

    assert "Failed to process bulk generation" in str(exc.value)
