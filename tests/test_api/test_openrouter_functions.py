import pytest
from unittest.mock import patch, MagicMock
import scripts.openrouter_functions as orf


@pytest.fixture(autouse=True)
def mock_streamlit_session(monkeypatch, request):
    # Only skip for tests that explicitly want no API key
    if "no_api_key" in request.keywords:
        return

    class FakeSession(dict):
        def get(self, key, default=None):
            if key == "OPENROUTER_API_KEY":
                return "fake-key"
            return super().get(key, default)

    monkeypatch.setattr(orf.st, "session_state", FakeSession())
    monkeypatch.setattr(orf.st, "secrets", {"OPENROUTER_API_KEY": "fake-key"})


@pytest.fixture
def mock_post():
    with patch("scripts.openrouter_functions.requests.post") as mock:
        mock.return_value = MagicMock(
            status_code=200,
            json=lambda: {"choices": [{"message": {"content": "mocked response"}}]},
        )
        yield mock


def test_enhance_script_calls_api_once(mock_post):
    # Should call API for each unique input
    success, result = orf.enhance_script_with_openrouter("test script", "enhance this")
    assert success
    assert result == "mocked response"
    assert mock_post.call_count == 1


def test_translate_script_calls_api_once(mock_post):
    result = orf.translate_script_with_openrouter("hello", "fr")
    assert result == "mocked response"
    assert mock_post.call_count == 1


def test_translate_script_with_custom_model(mock_post):
    """Test translation with custom model parameter."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"choices": [{"message": {"content": "mocked response"}}]},
    )
    result = orf.translate_script_with_openrouter("hello", "fr", model="custom-model")
    assert result == "mocked response"
    assert mock_post.call_count == 1
    # Verify model was passed
    call_data = mock_post.call_args[1]["json"]
    assert call_data["model"] == "custom-model"


def test_phonetic_conversion_calls_api_once(mock_post):
    result = orf.convert_word_to_phonetic_openrouter(
        "hello", "French", "eleven_monolingual_v1"
    )
    assert result == "mocked response"
    assert mock_post.call_count == 1


def test_error_handling_on_api_failure():
    with patch(
        "scripts.openrouter_functions.requests.post", side_effect=Exception("API down")
    ):
        success, result = orf.enhance_script_with_openrouter("fail script")
        assert not success
        assert "OpenRouter API error" in result


@pytest.mark.no_api_key
def test_no_api_key(monkeypatch):
    monkeypatch.setattr(orf, "get_openrouter_api_key", lambda: None)
    success, result = orf.enhance_script_with_openrouter("test script")
    assert not success
    assert "API key" in result or "not found" in result


# Note: If/when caching is implemented, add tests to ensure repeated identical calls do not trigger new requests.


def test_enhance_script_routes_to_v3_when_v3_model():
    """Test that enhancement routes to v3-specific function when v3 model is detected."""
    with patch("scripts.openrouter_functions.supports_audio_tags", return_value=True):
        with patch("scripts.openrouter_functions.enhance_script_for_v3") as mock_v3:
            mock_v3.return_value = (True, "v3 enhanced script")
            
            success, result = orf.enhance_script_with_openrouter(
                "test script", model_id="eleven_v3"
            )
            
            assert success
            assert result == "v3 enhanced script"
            mock_v3.assert_called_once_with("test script", "", None)


def test_enhance_script_routes_to_traditional_when_non_v3_model():
    """Test that enhancement uses traditional method when non-v3 model is detected."""
    with patch("scripts.openrouter_functions.supports_audio_tags", return_value=False):
        with patch("scripts.openrouter_functions.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"choices": [{"message": {"content": "traditional enhanced"}}]},
            )
            
            success, result = orf.enhance_script_with_openrouter(
                "test script", model_id="eleven_multilingual_v2"
            )
            
            assert success
            assert result == "traditional enhanced"
            mock_post.assert_called_once()


def test_enhance_script_routes_to_traditional_when_no_model_id():
    """Test that enhancement uses traditional method when no model_id is provided."""
    with patch("scripts.openrouter_functions.requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"choices": [{"message": {"content": "traditional enhanced"}}]},
        )
        
        success, result = orf.enhance_script_with_openrouter("test script")
        
        assert success
        assert result == "traditional enhanced"
        mock_post.assert_called_once()


def test_enhance_script_for_v3_includes_audio_tags_prompt(mock_post):
    """Test that v3 enhancement function uses Audio Tags prompt."""
    success, result = orf.enhance_script_for_v3("test script")
    
    assert success
    assert mock_post.call_count == 1
    
    # Verify the prompt contains Audio Tags references
    call_data = mock_post.call_args[1]["json"]
    user_message = call_data["messages"][1]["content"]
    
    assert "[excited]" in user_message or "Audio Tags" in user_message
    assert "square brackets" in user_message.lower() or "[tag]" in user_message.lower()
    assert "v3" in user_message.lower() or "Audio Tags" in user_message


def test_enhance_script_for_v3_passes_enhancement_prompt(mock_post):
    """Test that v3 enhancement function passes custom enhancement prompt."""
    custom_prompt = "Make it more dramatic"
    success, result = orf.enhance_script_for_v3("test script", enhancement_prompt=custom_prompt)
    
    assert success
    call_data = mock_post.call_args[1]["json"]
    user_message = call_data["messages"][1]["content"]
    
    assert custom_prompt in user_message
