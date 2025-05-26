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
