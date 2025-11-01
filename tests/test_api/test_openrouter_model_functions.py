"""Unit tests for OpenRouter model fetching, filtering, and search functions."""

import pytest
from unittest.mock import patch, MagicMock
import scripts.openrouter_functions as orf
from utils.error_handling import APIError


@pytest.fixture(autouse=True)
def mock_streamlit_session(monkeypatch):
    """Mock Streamlit session state and secrets."""
    class FakeSession(dict):
        def get(self, key, default=None):
            if key == "OPENROUTER_API_KEY":
                return "fake-key"
            return super().get(key, default)

    monkeypatch.setattr(orf.st, "session_state", FakeSession())
    monkeypatch.setattr(orf.st, "secrets", {"OPENROUTER_API_KEY": "fake-key"})


@pytest.fixture
def sample_models():
    """Sample model data for testing."""
    return [
        {
            "id": "openrouter/auto",
            "name": "Auto Model",
            "pricing": {"prompt": "0", "completion": "0"},
        },
        {
            "id": "anthropic/claude-3-opus",
            "name": "Claude 3 Opus",
            "pricing": {"prompt": "0.015", "completion": "0.075"},
        },
        {
            "id": "meta-llama/llama-3.1-8b-instruct:free",
            "name": "Llama 3.1 8B Free",
            "pricing": {"prompt": "0", "completion": "0"},
        },
        {
            "id": "google/gemini-pro",
            "name": "Gemini Pro",
            "pricing": {"prompt": "0.0005", "completion": "0.0015"},
        },
    ]


@pytest.fixture
def mock_get():
    """Mock requests.get for model fetching."""
    with patch("scripts.openrouter_functions.requests.get") as mock:
        yield mock


@pytest.fixture
def mock_post():
    """Mock requests.post for API calls."""
    with patch("scripts.openrouter_functions.requests.post") as mock:
        mock.return_value = MagicMock(
            status_code=200,
            json=lambda: {"choices": [{"message": {"content": "mocked response"}}]},
        )
        yield mock


def test_fetch_openrouter_models_success(mock_get, sample_models):
    """Test successful model fetching from OpenRouter API."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": sample_models}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    # Clear cache before testing
    orf.fetch_openrouter_models.clear()

    result = orf.fetch_openrouter_models()

    assert len(result) == 4
    assert result[0]["id"] == "openrouter/auto"
    mock_get.assert_called_once()
    assert "Authorization" in mock_get.call_args[1]["headers"]


def test_fetch_openrouter_models_api_error(mock_get):
    """Test error handling for API failures."""
    import requests
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    # Clear cache before testing
    orf.fetch_openrouter_models.clear()

    with pytest.raises(APIError) as exc_info:
        orf.fetch_openrouter_models()

    assert "Failed to fetch models" in str(exc_info.value)


def test_fetch_openrouter_models_empty_response(mock_get):
    """Test handling of empty API response."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": []}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    # Clear cache before testing
    orf.fetch_openrouter_models.clear()

    result = orf.fetch_openrouter_models()

    assert result == []


def test_fetch_openrouter_models_no_api_key(monkeypatch):
    """Test error when API key is missing."""
    monkeypatch.setattr(orf, "get_openrouter_api_key", lambda: None)

    # Clear cache before testing
    orf.fetch_openrouter_models.clear()

    with pytest.raises(APIError) as exc_info:
        orf.fetch_openrouter_models()

    assert "API key not found" in str(exc_info.value)


def test_fetch_openrouter_models_caching(mock_get, sample_models):
    """Test that caching decorator is applied and works."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": sample_models}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    # Clear cache before testing
    orf.fetch_openrouter_models.clear()

    # First call
    result1 = orf.fetch_openrouter_models()
    assert mock_get.call_count == 1

    # Second call should use cache
    result2 = orf.fetch_openrouter_models()
    assert mock_get.call_count == 1  # Still 1, cached
    assert result1 == result2


def test_identify_free_models(sample_models):
    """Test identification of free models."""
    # Convert pricing strings to numbers for test
    models = [
        {
            "id": "model1",
            "pricing": {"prompt": 0, "completion": 0},
        },
        {
            "id": "model2",
            "pricing": {"prompt": 0.01, "completion": 0.02},
        },
        {
            "id": "model3",
            "pricing": {"prompt": 0, "completion": 0},
        },
        {
            "id": "model4",
            "pricing": {"prompt": 0.001, "completion": 0},
        },
    ]

    free_models = orf.identify_free_models(models)

    assert len(free_models) == 2
    assert free_models[0]["id"] == "model1"
    assert free_models[1]["id"] == "model3"


def test_identify_free_models_mixed_pricing():
    """Test free model identification with various pricing structures."""
    models = [
        {"id": "free1", "pricing": {"prompt": 0, "completion": 0}},
        {"id": "paid1", "pricing": {"prompt": 0.001, "completion": 0.002}},
        {"id": "free2", "pricing": {"prompt": 0, "completion": 0}},
        {"id": "partial1", "pricing": {"prompt": 0, "completion": 0.01}},
        {"id": "partial2", "pricing": {"prompt": 0.01, "completion": 0}},
        {"id": "missing_pricing", "pricing": {}},
    ]

    free_models = orf.identify_free_models(models)

    assert len(free_models) == 2
    assert free_models[0]["id"] == "free1"
    assert free_models[1]["id"] == "free2"


def test_filter_free_models():
    """Test filtering models by free status."""
    models = [
        {"id": "free1", "pricing": {"prompt": 0, "completion": 0}},
        {"id": "paid1", "pricing": {"prompt": 0.01, "completion": 0.02}},
        {"id": "free2", "pricing": {"prompt": 0, "completion": 0}},
    ]

    # Test with show_free_only=False
    result_all = orf.filter_free_models(models, show_free_only=False)
    assert len(result_all) == 3

    # Test with show_free_only=True
    result_free = orf.filter_free_models(models, show_free_only=True)
    assert len(result_free) == 2
    assert all(m["id"] in ["free1", "free2"] for m in result_free)


def test_search_models_fuzzy_exact_match(sample_models):
    """Test exact model name matching."""
    result = orf.search_models_fuzzy(sample_models, "Claude 3 Opus")

    assert len(result) > 0
    assert result[0]["id"] == "anthropic/claude-3-opus"


def test_search_models_fuzzy_partial_match(sample_models):
    """Test partial name matching."""
    result = orf.search_models_fuzzy(sample_models, "Claude")

    assert len(result) > 0
    assert any("claude" in m["id"].lower() or "claude" in m.get("name", "").lower() for m in result)


def test_search_models_fuzzy_typo_tolerance(sample_models):
    """Test fuzzy matching with typos."""
    # Test with typo "clode" instead of "claude"
    result = orf.search_models_fuzzy(sample_models, "clode")

    assert len(result) > 0
    # Should still find claude models despite typo
    assert any("claude" in m["id"].lower() for m in result)


def test_search_models_fuzzy_case_insensitive(sample_models):
    """Test case-insensitive matching."""
    result_lower = orf.search_models_fuzzy(sample_models, "claude")
    result_upper = orf.search_models_fuzzy(sample_models, "CLAUDE")
    result_mixed = orf.search_models_fuzzy(sample_models, "ClAuDe")

    # All should return same results
    assert len(result_lower) == len(result_upper) == len(result_mixed)
    assert result_lower[0]["id"] == result_upper[0]["id"]


def test_search_models_fuzzy_empty_query(sample_models):
    """Test behavior with empty search query."""
    result = orf.search_models_fuzzy(sample_models, "")

    assert len(result) == len(sample_models)
    assert result == sample_models


def test_search_models_fuzzy_no_match(sample_models):
    """Test behavior when no models match."""
    # Use a query that definitely won't match anything, with higher threshold
    result = orf.search_models_fuzzy(sample_models, "zzzzzzzzzzzzzzzzzzz", min_score=0.5)

    assert len(result) == 0


def test_combined_fuzzy_search_and_free_filter(sample_models):
    """Test combining fuzzy search and free filter."""
    # Convert pricing to numbers for test
    models = [
        {"id": "free-model-1", "name": "Free Model One", "pricing": {"prompt": 0, "completion": 0}},
        {"id": "paid-model-1", "name": "Paid Model One", "pricing": {"prompt": 0.01, "completion": 0.02}},
        {"id": "free-model-2", "name": "Free Model Two", "pricing": {"prompt": 0, "completion": 0}},
    ]

    # First filter by free
    free_models = orf.filter_free_models(models, show_free_only=True)
    assert len(free_models) == 2

    # Then search within free models for "one" (should match "One" in name)
    result = orf.search_models_fuzzy(free_models, "one")

    # Should find at least the model with "One" in the name
    assert len(result) >= 1
    assert any("one" in m.get("name", "").lower() or "model-1" in m.get("id", "") for m in result)


def test_session_state_initialization():
    """Test that session state variables would be initialized correctly."""
    # This is more of an integration test concept
    # In unit tests, we test the functions independently
    # Session state initialization is tested in UI tests
    assert True  # Placeholder - actual session state testing done in UI tests


def test_translate_with_custom_model(mock_post):
    """Test translation with custom model selection."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"choices": [{"message": {"content": "Bonjour"}}]},
    )

    result = orf.translate_script_with_openrouter(
        "Hello", "French", model="anthropic/claude-3-opus"
    )

    assert result == "Bonjour"
    assert mock_post.call_count == 1
    # Verify model was passed in request
    call_data = mock_post.call_args[1]["json"]
    assert call_data["model"] == "anthropic/claude-3-opus"


def test_translate_with_default_model(mock_post):
    """Test backward compatibility - translation without model uses default."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"choices": [{"message": {"content": "Hola"}}]},
    )

    result = orf.translate_script_with_openrouter("Hello", "Spanish")

    assert result == "Hola"
    # Verify default model was used
    call_data = mock_post.call_args[1]["json"]
    assert call_data["model"] == orf.DEFAULT_MODEL

