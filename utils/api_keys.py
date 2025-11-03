"""API key management utilities for ElevenTools.

This module provides centralized functions for retrieving API keys from session state
or Streamlit secrets, supporting both local development and cloud deployment scenarios.
"""

from typing import Optional
import streamlit as st


def get_elevenlabs_api_key() -> Optional[str]:
    """Get ElevenLabs API key from session state or secrets.
    
    Checks session state first (for user-entered keys), then falls back to
    st.secrets (for local development or Streamlit Cloud secrets).
    
    This approach supports:
    - Multi-user cloud deployment without authentication layer
    - Per-user API keys via session storage
    - Local development via .streamlit/secrets.toml
    - Streamlit Cloud deployment via dashboard secrets
    
    Returns:
        Optional[str]: The API key if found, None otherwise.
    """
    return st.session_state.get("ELEVENLABS_API_KEY") or st.secrets.get(
        "ELEVENLABS_API_KEY"
    )


def get_openrouter_api_key() -> Optional[str]:
    """Get OpenRouter API key from session state or secrets.
    
    Checks session state first (for user-entered keys), then falls back to
    st.secrets (for local development or Streamlit Cloud secrets).
    
    Returns:
        Optional[str]: The API key if found, None otherwise.
    """
    return st.session_state.get("OPENROUTER_API_KEY") or st.secrets.get(
        "OPENROUTER_API_KEY"
    )

