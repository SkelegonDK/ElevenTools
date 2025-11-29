"""API key management utilities for ElevenTools.

This module provides centralized functions for retrieving API keys from session state
or Streamlit secrets, supporting both local development and cloud deployment scenarios.
"""

import streamlit as st


def get_api_key(key_name: str) -> str | None:
    """Get API key from session state or secrets.

    Generic function for retrieving API keys that checks session state first
    (for user-entered keys), then falls back to st.secrets (for local development
    or Streamlit Cloud secrets).

    This approach supports:
    - Multi-user cloud deployment without authentication layer
    - Per-user API keys via session storage
    - Local development via .streamlit/secrets.toml
    - Streamlit Cloud deployment via dashboard secrets

    Args:
        key_name (str): The name of the API key to retrieve (e.g., "ELEVENLABS_API_KEY").

    Returns:
        Optional[str]: The API key if found, None otherwise.
    """
    return st.session_state.get(key_name) or st.secrets.get(key_name)


def get_elevenlabs_api_key() -> str | None:
    """Get ElevenLabs API key from session state or secrets.

    Checks session state first (for user-entered keys), then falls back to
    st.secrets (for local development or Streamlit Cloud secrets).

    Returns:
        Optional[str]: The API key if found, None otherwise.
    """
    return get_api_key("ELEVENLABS_API_KEY")


def get_openrouter_api_key() -> str | None:
    """Get OpenRouter API key from session state or secrets.

    Checks session state first (for user-entered keys), then falls back to
    st.secrets (for local development or Streamlit Cloud secrets).

    Returns:
        Optional[str]: The API key if found, None otherwise.
    """
    return get_api_key("OPENROUTER_API_KEY")
