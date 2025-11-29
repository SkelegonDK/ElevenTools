"""Unit tests for API key management utilities."""

from unittest.mock import MagicMock, patch

from utils.api_keys import (
    get_api_key,
    get_elevenlabs_api_key,
    get_openrouter_api_key,
)


def test_get_elevenlabs_api_key_from_session_state():
    """Test that session state key is returned when available."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {"ELEVENLABS_API_KEY": "session-key-123"}
        mock_st.secrets = {}

        result = get_elevenlabs_api_key()
        assert result == "session-key-123"


def test_get_elevenlabs_api_key_from_secrets_fallback():
    """Test that secrets key is returned when session state is empty."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {}
        mock_st.secrets = {"ELEVENLABS_API_KEY": "secrets-key-456"}

        result = get_elevenlabs_api_key()
        assert result == "secrets-key-456"


def test_get_elevenlabs_api_key_session_state_priority():
    """Test that session state takes priority over secrets."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {"ELEVENLABS_API_KEY": "session-key-789"}
        mock_st.secrets = {"ELEVENLABS_API_KEY": "secrets-key-999"}

        result = get_elevenlabs_api_key()
        assert result == "session-key-789"


def test_get_elevenlabs_api_key_missing():
    """Test that None is returned when no key is available."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {}
        mock_st.secrets = {}

        result = get_elevenlabs_api_key()
        assert result is None


def test_get_elevenlabs_api_key_secrets_get_method():
    """Test that secrets.get() is used (handles KeyError gracefully)."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {}
        # Mock secrets as dict-like object with .get() method
        mock_secrets = MagicMock()
        mock_secrets.get.return_value = "secrets-key-from-get"
        mock_st.secrets = mock_secrets

        result = get_elevenlabs_api_key()
        assert result == "secrets-key-from-get"
        mock_secrets.get.assert_called_once_with("ELEVENLABS_API_KEY")


def test_get_openrouter_api_key_from_session_state():
    """Test that session state key is returned when available."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {"OPENROUTER_API_KEY": "session-key-123"}
        mock_st.secrets = {}

        result = get_openrouter_api_key()
        assert result == "session-key-123"


def test_get_openrouter_api_key_from_secrets_fallback():
    """Test that secrets key is returned when session state is empty."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {}
        mock_st.secrets = {"OPENROUTER_API_KEY": "secrets-key-456"}

        result = get_openrouter_api_key()
        assert result == "secrets-key-456"


def test_get_openrouter_api_key_session_state_priority():
    """Test that session state takes priority over secrets."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {"OPENROUTER_API_KEY": "session-key-789"}
        mock_st.secrets = {"OPENROUTER_API_KEY": "secrets-key-999"}

        result = get_openrouter_api_key()
        assert result == "session-key-789"


def test_get_openrouter_api_key_missing():
    """Test that None is returned when no key is available."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {}
        mock_st.secrets = {}

        result = get_openrouter_api_key()
        assert result is None


def test_get_api_key_generic_from_session_state():
    """Test generic get_api_key function with session state."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {"CUSTOM_API_KEY": "session-key-123"}
        mock_st.secrets = {}

        result = get_api_key("CUSTOM_API_KEY")
        assert result == "session-key-123"


def test_get_api_key_generic_from_secrets_fallback():
    """Test generic get_api_key function with secrets fallback."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {}
        mock_st.secrets = {"CUSTOM_API_KEY": "secrets-key-456"}

        result = get_api_key("CUSTOM_API_KEY")
        assert result == "secrets-key-456"


def test_get_api_key_generic_session_state_priority():
    """Test that session state takes priority in generic function."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {"CUSTOM_API_KEY": "session-key-789"}
        mock_st.secrets = {"CUSTOM_API_KEY": "secrets-key-999"}

        result = get_api_key("CUSTOM_API_KEY")
        assert result == "session-key-789"


def test_get_api_key_generic_missing():
    """Test generic get_api_key returns None when key is missing."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {}
        mock_st.secrets = {}

        result = get_api_key("NONEXISTENT_KEY")
        assert result is None


def test_get_api_key_handles_secrets_get_method():
    """Test that get_api_key uses secrets.get() safely."""
    with patch("utils.api_keys.st") as mock_st:
        mock_st.session_state = {}
        mock_secrets = MagicMock()
        mock_secrets.get.return_value = None  # Key doesn't exist
        mock_st.secrets = mock_secrets

        result = get_api_key("MISSING_KEY")
        assert result is None
        mock_secrets.get.assert_called_once_with("MISSING_KEY")
