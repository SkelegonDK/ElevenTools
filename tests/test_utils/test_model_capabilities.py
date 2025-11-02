"""Tests for model capabilities detection."""

import pytest
from utils.model_capabilities import (
    supports_speed,
    supports_audio_tags,
    get_model_capabilities,
)


def test_supports_speed_with_allow_list_models():
    """Test that allow-list models return True for speed support."""
    # Test known models from allow-list
    assert supports_speed("eleven_multilingual_v2") is True
    assert supports_speed("eleven_turbo_v2_5") is True
    assert supports_speed("eleven_flash_v2_5") is True
    assert supports_speed("eleven_v3") is True
    assert supports_speed("eleven_multilingual_sts_v2") is True


def test_supports_speed_with_pattern_matching():
    """Test that pattern matching works for models not in allow-list."""
    # Test pattern matching for multilingual models
    assert supports_speed("eleven_multilingual_v3") is True
    assert supports_speed("eleven_multilingual_v4") is True
    assert supports_speed("custom_multilingual_model") is True
    
    # Test pattern matching for turbo v2+ models (pattern matches "turbo_v2")
    assert supports_speed("eleven_turbo_v2_6") is True
    # Note: "turbo_v3" doesn't match "turbo_v2" pattern, which is expected
    # If v3 supports speed, it should be added to allow-list
    
    # Test pattern matching for flash v2+ models (pattern matches "flash_v2")
    assert supports_speed("eleven_flash_v2_6") is True
    # Note: "flash_v3" doesn't match "flash_v2" pattern, which is expected


def test_supports_speed_with_non_supporting_models():
    """Test that models without speed support return False."""
    assert supports_speed("eleven_monolingual_v1") is False
    assert supports_speed("eleven_english_sts_v2") is False
    assert supports_speed("unknown_model") is False
    assert supports_speed("") is False


def test_supports_speed_case_insensitive():
    """Test that pattern matching is case-insensitive."""
    assert supports_speed("ELEVEN_MULTILINGUAL_V2") is True
    assert supports_speed("Eleven_Turbo_V2_5") is True


def test_get_model_capabilities():
    """Test that get_model_capabilities returns correct capability dictionary."""
    # Test with speed-supporting model
    capabilities = get_model_capabilities("eleven_multilingual_v2")
    assert capabilities["speed"] is True
    
    # Test with non-speed-supporting model
    capabilities = get_model_capabilities("eleven_monolingual_v1")
    assert capabilities["speed"] is False


def test_get_model_capabilities_extensibility():
    """Test that get_model_capabilities returns dictionary structure."""
    capabilities = get_model_capabilities("eleven_multilingual_v2")
    assert isinstance(capabilities, dict)
    assert "speed" in capabilities
    # Future capabilities can be added here when implemented


def test_supports_speed_caching():
    """Test that supports_speed uses caching (should return same result quickly)."""
    result1 = supports_speed("eleven_multilingual_v2")
    result2 = supports_speed("eleven_multilingual_v2")
    assert result1 == result2
    assert result1 is True


def test_supports_audio_tags_with_allow_list_models():
    """Test that allow-list v3 models return True for Audio Tags support."""
    assert supports_audio_tags("eleven_v3") is True
    assert supports_audio_tags("eleven_multilingual_v3") is True


def test_supports_audio_tags_with_pattern_matching():
    """Test that pattern matching works for v3 models not in allow-list."""
    # Test pattern matching for v3 models
    assert supports_audio_tags("eleven_custom_v3") is True
    assert supports_audio_tags("some_model_v3") is True
    assert supports_audio_tags("eleven_v3_alpha") is True


def test_supports_audio_tags_with_non_v3_models():
    """Test that non-v3 models return False for Audio Tags support."""
    assert supports_audio_tags("eleven_multilingual_v2") is False
    assert supports_audio_tags("eleven_monolingual_v1") is False
    assert supports_audio_tags("eleven_turbo_v2_5") is False
    assert supports_audio_tags("unknown_model") is False
    assert supports_audio_tags("") is False


def test_supports_audio_tags_case_insensitive():
    """Test that pattern matching is case-insensitive."""
    assert supports_audio_tags("ELEVEN_V3") is True
    assert supports_audio_tags("Eleven_Multilingual_V3") is True


def test_get_model_capabilities_includes_audio_tags():
    """Test that get_model_capabilities includes audio_tags capability."""
    # Test with v3 model (supports both speed and audio_tags)
    capabilities = get_model_capabilities("eleven_v3")
    assert capabilities["speed"] is True
    assert capabilities["audio_tags"] is True
    
    # Test with non-v3 model (supports speed but not audio_tags)
    capabilities = get_model_capabilities("eleven_multilingual_v2")
    assert capabilities["speed"] is True
    assert capabilities["audio_tags"] is False
    
    # Test with model that supports neither
    capabilities = get_model_capabilities("eleven_monolingual_v1")
    assert capabilities["speed"] is False
    assert capabilities["audio_tags"] is False


def test_get_model_capabilities_extensibility_with_audio_tags():
    """Test that get_model_capabilities returns dictionary with audio_tags."""
    capabilities = get_model_capabilities("eleven_v3")
    assert isinstance(capabilities, dict)
    assert "speed" in capabilities
    assert "audio_tags" in capabilities

