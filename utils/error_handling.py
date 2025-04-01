"""Error handling utilities for ElevenTools."""

from typing import Optional, Any, Tuple
import logging
import traceback
import streamlit as st


class ElevenToolsError(Exception):
    """Base exception for ElevenTools."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class APIError(ElevenToolsError):
    """Exception for API-related errors."""

    pass


class ValidationError(ElevenToolsError):
    """Exception for input validation errors."""

    pass


class ConfigurationError(ElevenToolsError):
    """Exception for configuration-related errors."""

    pass


def handle_error(error: Exception, show_traceback: bool = False) -> Tuple[bool, str]:
    """Handle exceptions and return appropriate error messages.

    Args:
        error: The exception to handle
        show_traceback: Whether to include traceback in logging

    Returns:
        Tuple of (success, error_message)
    """
    if show_traceback:
        logging.error(f"Error occurred: {str(error)}\n{traceback.format_exc()}")
    else:
        logging.error(f"Error occurred: {str(error)}")

    if isinstance(error, APIError):
        st.error("🔌 API Error: " + error.message)
        if error.details:
            st.error("Details: " + error.details)
    elif isinstance(error, ValidationError):
        st.warning("⚠️ Validation Error: " + error.message)
        if error.details:
            st.info("Help: " + error.details)
    elif isinstance(error, ConfigurationError):
        st.error("⚙️ Configuration Error: " + error.message)
        if error.details:
            st.info("Fix: " + error.details)
    else:
        st.error("❌ An unexpected error occurred: " + str(error))

    return False, str(error)


def validate_api_key(api_key: Optional[str], service_name: str) -> None:
    """Validate API key presence and format.

    Args:
        api_key: The API key to validate
        service_name: Name of the service (e.g., 'ElevenLabs', 'OpenAI')

    Raises:
        ConfigurationError: If API key is invalid
    """
    if not api_key:
        raise ConfigurationError(
            f"{service_name} API key not found",
            f"Please add your {service_name} API key to .streamlit/secrets.toml",
        )
    if api_key.startswith("sk-dummy"):
        raise ConfigurationError(
            f"Invalid {service_name} API key",
            f"Please replace the dummy {service_name} API key with a valid one",
        )


class ProgressManager:
    """Manage progress bars and status messages in Streamlit."""

    def __init__(self, total_steps: int = 100):
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.total_steps = total_steps
        self._current_step = 0

    def update(self, step: int, message: str) -> None:
        """Update progress bar and status message.

        Args:
            step: Current step (0-100)
            message: Status message to display
        """
        progress = min(step / self.total_steps, 1.0)
        self.progress_bar.progress(progress)
        self.status_text.text(f"{message} ({progress:.0%})")

    def complete(self, success: bool = True) -> None:
        """Complete the progress tracking.

        Args:
            success: Whether the operation was successful
        """
        if success:
            self.progress_bar.progress(1.0)
            self.status_text.success("✅ Operation completed successfully!")
        else:
            self.status_text.error("❌ Operation failed")
        self.clear()

    def clear(self) -> None:
        """Clear the progress bar and status message."""
        self.progress_bar.empty()
        self.status_text.empty()
