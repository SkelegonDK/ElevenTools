"""Error handling utilities for ElevenTools."""

import logging
import time
import traceback

import streamlit as st

try:
    import requests
except ImportError:
    requests = None


class ElevenToolsError(Exception):
    """Base exception for ElevenTools."""

    def __init__(self, message: str, details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class APIError(ElevenToolsError):
    """Exception for API-related errors."""

    pass


class ValidationError(ElevenToolsError):
    """Exception for input validation errors."""

    pass


class ConfigurationError(ElevenToolsError):
    """Exception for configuration-related errors."""

    pass


def handle_error(error: Exception, show_traceback: bool = False) -> tuple[bool, str]:
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


def validate_api_key(api_key: str | None, service_name: str) -> None:
    """Validate API key presence and format.

    Args:
        api_key: The API key to validate
        service_name: Name of the service (e.g., 'ElevenLabs', 'OpenRouter')

    Raises:
        ConfigurationError: If API key is invalid
    """
    if not api_key:
        raise ConfigurationError(
            f"{service_name} API key not found",
            f"Please add your {service_name} API key via the Settings page or configure it in Streamlit secrets.",
        )
    if api_key.startswith("sk-dummy"):
        raise ConfigurationError(
            f"Invalid {service_name} API key",
            f"Please replace the dummy {service_name} API key with a valid one via the Settings page.",
        )


def test_api_key_actual(api_key: str, service_name: str) -> tuple[bool, str | None]:
    """Test API key by making an actual API call.

    This function makes a lightweight API call to verify the key works,
    not just that it has the correct format.

    Args:
        api_key: The API key to test
        service_name: Name of the service (e.g., 'ElevenLabs', 'OpenRouter')

    Returns:
        Tuple of (is_valid, error_message). is_valid is True if the key works,
        False otherwise. error_message is None if valid, otherwise contains the error.
    """
    if not requests:
        # If requests is not available, fall back to format validation
        try:
            validate_api_key(api_key, service_name)
            return True, None
        except ConfigurationError as e:
            return False, str(e)

    try:
        if service_name == "ElevenLabs":
            # Test by fetching models (lightweight endpoint)
            url = "https://api.elevenlabs.io/v1/models"
            headers = {"xi-api-key": api_key}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return True, None
        elif service_name == "OpenRouter":
            # Test by fetching models (lightweight endpoint)
            url = "https://openrouter.ai/api/v1/models"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return True, None
        else:
            # Unknown service, fall back to format validation
            try:
                validate_api_key(api_key, service_name)
                return True, None
            except ConfigurationError as e:
                return False, str(e)
    except requests.exceptions.HTTPError as e:
        # Check for specific error codes
        if e.response.status_code == 401:
            return False, "Invalid or expired API key"
        elif e.response.status_code == 403:
            return False, "API key lacks required permissions"
        else:
            return False, f"API error: {e.response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Request timed out - please try again"
    except requests.exceptions.RequestException as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


class ProgressManager:
    """Manage progress bars and status messages in Streamlit."""

    def __init__(self, total_steps: int = 100) -> None:
        """Initialize progress manager.

        Args:
            total_steps (int, optional): Total number of steps for progress tracking. Defaults to 100.
        """
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
