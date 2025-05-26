"""Shared test fixtures for ElevenTools tests."""

import pytest
from unittest.mock import patch


@pytest.fixture
def mock_requests():
    """Mock requests for API tests."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        yield mock_get, mock_post


@pytest.fixture
def mock_file_operations():
    """Mock file operations."""
    with patch("builtins.open", create=True) as mock_open:
        yield mock_open


@pytest.fixture
def sample_voice_settings():
    """Sample voice settings for tests."""
    return {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for bulk generation tests."""
    return "text,filename\nHello {name},greeting_{name}\nWelcome to {place},welcome_{place}"
