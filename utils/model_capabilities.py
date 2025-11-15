"""Model capabilities detection for ElevenTools.

This module provides functions to determine which voice settings are supported
by different ElevenLabs models. Uses allow-list and pattern matching for
flexible capability detection.
"""


from utils.caching import st_cache

# Allow-list of model IDs that explicitly support speed control
# Based on ElevenLabs API documentation and MCP verification
SPEED_SUPPORTED_MODELS = {
    "eleven_multilingual_v2",
    "eleven_turbo_v2_5",
    "eleven_flash_v2_5",
    "eleven_v3",
    "eleven_multilingual_sts_v2",
}

# Allow-list of model IDs that support Audio Tags (v3 models)
# Based on ElevenLabs v3 documentation: https://elevenlabs.io/blog/v3-audiotags
AUDIO_TAGS_SUPPORTED_MODELS = {
    "eleven_v3",
    "eleven_multilingual_v3",
}


# Pattern-based detection for models that might support speed
# These patterns help identify models that likely support speed without
# needing to add them explicitly to the allow-list
SPEED_SUPPORT_PATTERNS = [
    "multilingual",  # Multilingual models typically support speed
    "turbo_v2",  # Turbo v2+ models support speed
    "flash_v2",  # Flash v2+ models support speed
]

# Pattern-based detection for models that might support Audio Tags
# v3 models use a specific naming pattern
AUDIO_TAGS_SUPPORT_PATTERNS = [
    "_v3",  # v3 models support Audio Tags
]


@st_cache(ttl_minutes=60)
def supports_speed(model_id: str) -> bool:
    """Check if a model supports speed control.

    Uses allow-list first, then falls back to pattern matching for
    unknown models. Results are cached for performance.

    Args:
        model_id (str): The model ID to check (e.g., "eleven_multilingual_v2").

    Returns:
        bool: True if the model supports speed control, False otherwise.

    Examples:
        >>> supports_speed("eleven_multilingual_v2")
        True
        >>> supports_speed("eleven_monolingual_v1")
        False
        >>> supports_speed("eleven_multilingual_v3")  # Pattern match
        True
    """
    if not model_id:
        return False

    # Check allow-list first (most reliable)
    if model_id in SPEED_SUPPORTED_MODELS:
        return True

    # Fall back to pattern matching for unknown models
    model_id_lower = model_id.lower()
    for pattern in SPEED_SUPPORT_PATTERNS:
        if pattern in model_id_lower:
            return True

    return False


@st_cache(ttl_minutes=60)
def supports_audio_tags(model_id: str) -> bool:
    """Check if a model supports Audio Tags (v3 feature).

    Audio Tags are square-bracketed tags like [excited], [whispers], [sighs]
    that provide expressive control over v3 model speech generation.
    Only v3 models support Audio Tags.

    Uses allow-list first, then falls back to pattern matching for
    unknown models. Results are cached for performance.

    Args:
        model_id (str): The model ID to check (e.g., "eleven_v3").

    Returns:
        bool: True if the model supports Audio Tags, False otherwise.

    Examples:
        >>> supports_audio_tags("eleven_v3")
        True
        >>> supports_audio_tags("eleven_multilingual_v3")
        True
        >>> supports_audio_tags("eleven_multilingual_v2")
        False
        >>> supports_audio_tags("eleven_monolingual_v1")
        False
    """
    if not model_id:
        return False

    # Check allow-list first (most reliable)
    if model_id in AUDIO_TAGS_SUPPORTED_MODELS:
        return True

    # Fall back to pattern matching for unknown models
    model_id_lower = model_id.lower()
    for pattern in AUDIO_TAGS_SUPPORT_PATTERNS:
        if pattern in model_id_lower:
            return True

    return False


@st_cache(ttl_minutes=60)
def get_model_capabilities(model_id: str) -> dict[str, bool]:
    """Get all capabilities for a given model.

    Returns a dictionary of capability flags. Currently supports:
    - speed: Whether the model supports speed control
    - audio_tags: Whether the model supports Audio Tags (v3 feature)

    This function is designed to be extensible for future capabilities
    (e.g., style, advanced settings).

    Args:
        model_id (str): The model ID to check.

    Returns:
        Dict[str, bool]: Dictionary with capability flags.
            Example: {"speed": True, "audio_tags": True}

    Examples:
        >>> get_model_capabilities("eleven_multilingual_v2")
        {"speed": True, "audio_tags": False}
        >>> get_model_capabilities("eleven_v3")
        {"speed": True, "audio_tags": True}
        >>> get_model_capabilities("eleven_monolingual_v1")
        {"speed": False, "audio_tags": False}
    """
    return {
        "speed": supports_speed(model_id),
        "audio_tags": supports_audio_tags(model_id),
        # Future capabilities can be added here:
        # "style": supports_style(model_id),
        # "advanced_settings": supports_advanced_settings(model_id),
    }
