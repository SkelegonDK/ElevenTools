from typing import Dict, List

import pytest

from scripts import openrouter_functions as orf


@pytest.mark.core_suite
def test_enhance_script_with_openrouter_routes_v3(mocker):
    mocker.patch("scripts.openrouter_functions.supports_audio_tags", return_value=True)
    mock_enhance_v3 = mocker.patch(
        "scripts.openrouter_functions.enhance_script_for_v3",
        return_value=(True, "[excited] Hello!"),
    )
    mocker.patch("scripts.openrouter_functions.get_openrouter_api_key", return_value="sk")

    success, result = orf.enhance_script_with_openrouter(
        "Hello", enhancement_prompt="Add energy", model_id="eleven_v3"
    )

    assert success is True
    assert "[excited]" in result
    mock_enhance_v3.assert_called_once()


@pytest.mark.core_suite
def test_enhance_script_with_openrouter_missing_api_key(mocker):
    mocker.patch("scripts.openrouter_functions.supports_audio_tags", return_value=False)
    mocker.patch("scripts.openrouter_functions.get_openrouter_api_key", return_value=None)

    success, message = orf.enhance_script_with_openrouter("Hello there")

    assert success is False
    assert "API key not found" in message


@pytest.mark.core_suite
def test_get_openrouter_response_success(mocker):
    mock_response = mocker.Mock()
    mock_response.raise_for_status = mocker.Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Processed answer"}}]
    }
    mocker.patch("scripts.openrouter_functions.get_openrouter_api_key", return_value="sk")
    mocker.patch(
        "scripts.openrouter_functions.requests.post",
        return_value=mock_response,
    )

    result = orf.get_openrouter_response("Hello?")

    assert result == "Processed answer"


@pytest.mark.core_suite
def test_get_openrouter_response_error(mocker):
    mocker.patch("scripts.openrouter_functions.get_openrouter_api_key", return_value="sk")
    mocker.patch(
        "scripts.openrouter_functions.requests.post",
        side_effect=Exception("Timeout"),
    )

    result = orf.get_openrouter_response("Hello?")

    assert "OpenRouter API error" in result


@pytest.mark.core_suite
def test_translate_script_with_openrouter_uses_default_model(mocker):
    mocker.patch(
        "scripts.openrouter_functions.get_default_translation_model",
        return_value="model-default",
    )
    call_spy = mocker.patch(
        "scripts.openrouter_functions.get_openrouter_response",
        return_value="Bonjour le monde",
    )

    result = orf.translate_script_with_openrouter("Hello world", "French")

    assert result == "Bonjour le monde"
    call_spy.assert_called_once()
    _, kwargs = call_spy.call_args
    assert kwargs["model"] == "model-default"


@pytest.mark.core_suite
def test_identify_and_filter_free_models():
    models: List[Dict[str, object]] = [
        {"id": "minimax/minimax-m2:free", "pricing": {"prompt": 0, "completion": 0}},
        {"id": "provider/model-paid", "pricing": {"prompt": 0.001, "completion": 0.001}},
        {"id": "provider/alt", "pricing": {"prompt": 0, "completion": 0}},
    ]

    free = orf.identify_free_models(models)
    assert len(free) == 2
    assert all(model in free for model in [models[0], models[2]])

    filtered = orf.filter_free_models(models, show_free_only=True)
    assert filtered == free

