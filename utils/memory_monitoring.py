"""Memory monitoring utilities for production debugging.

This module provides utilities for monitoring memory usage and session state
sizes to help identify memory leaks and optimize resource usage.
"""

import logging
import sys
from typing import Any

import streamlit as st

logger = logging.getLogger(__name__)


def get_session_state_size(
    session_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate the approximate size of session state in bytes.

    Args:
        session_state: Streamlit session state dict (defaults to st.session_state)

    Returns:
        Dictionary with size information:
        - total_size: Total approximate size in bytes
        - item_count: Number of items in session state
        - largest_items: List of largest items with their sizes
    """
    if session_state is None:
        session_state = st.session_state

    total_size = 0
    item_sizes = {}

    for key, value in session_state.items():
        try:
            # Estimate size using sys.getsizeof
            size = sys.getsizeof(value)

            # For lists/dicts, add size of items
            if isinstance(value, (list, dict)):
                if isinstance(value, list):
                    for item in value:
                        size += sys.getsizeof(item)
                elif isinstance(value, dict):
                    for v in value.values():
                        size += sys.getsizeof(v)

            item_sizes[key] = size
            total_size += size
        except Exception:
            # Skip items we can't measure
            item_sizes[key] = 0

    # Get top 5 largest items
    largest_items = sorted(item_sizes.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_size": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "item_count": len(session_state),
        "largest_items": [
            (key, size, round(size / (1024 * 1024), 2)) for key, size in largest_items
        ],
    }


def log_session_state_memory(
    level: str = "INFO", session_state: dict[str, Any] | None = None
) -> None:
    """Log session state memory usage for debugging.

    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING") - defaults to "INFO"
        session_state: Streamlit session state dict (defaults to st.session_state)
    """
    try:
        size_info = get_session_state_size(session_state)

        log_message = (
            f"Session state memory: {size_info['total_size_mb']} MB "
            f"({size_info['item_count']} items)"
        )

        if level.upper() == "DEBUG":
            logger.debug(log_message)
            logger.debug(f"Largest items: {size_info['largest_items']}")
        elif level.upper() == "WARNING":
            logger.warning(log_message)
            if size_info["total_size_mb"] > 50:  # Warn if over 50MB
                logger.warning(
                    f"High memory usage detected! Largest items: {size_info['largest_items']}"
                )
        else:
            logger.info(log_message)
            if size_info["total_size_mb"] > 50:
                logger.warning(
                    f"High memory usage detected! Largest items: {size_info['largest_items']}"
                )
    except Exception as e:
        logger.error(f"Error logging session state memory: {e}")


def check_list_size_limit(
    list_key: str,
    max_size: int,
    session_state: dict[str, Any] | None = None,
    log_warning: bool = True,
) -> bool:
    """Check if a session state list exceeds size limit and log warning.

    Args:
        list_key: Key of the list in session state
        max_size: Maximum allowed size
        session_state: Streamlit session state dict (defaults to st.session_state)
        log_warning: Whether to log a warning if limit is exceeded

    Returns:
        True if within limit, False if exceeded
    """
    if session_state is None:
        session_state = st.session_state

    if list_key not in session_state:
        return True

    list_value = session_state[list_key]
    if not isinstance(list_value, list):
        return True

    current_size = len(list_value)
    within_limit = current_size <= max_size

    if not within_limit and log_warning:
        logger.warning(
            f"Session state list '{list_key}' exceeds limit: "
            f"{current_size}/{max_size} items"
        )

    return within_limit


def monitor_memory_usage(
    operation_name: str,
    session_state: dict[str, Any] | None = None,
    log_before: bool = True,
    log_after: bool = True,
) -> dict[str, Any]:
    """Context manager-like function to monitor memory before/after an operation.

    Usage:
        before_info = monitor_memory_usage("operation_name", log_before=True, log_after=False)
        # ... perform operation ...
        after_info = monitor_memory_usage("operation_name", log_before=False, log_after=True)
        delta = after_info['total_size_mb'] - before_info['total_size_mb']

    Args:
        operation_name: Name of the operation being monitored
        session_state: Streamlit session state dict (defaults to st.session_state)
        log_before: Whether to log memory before operation
        log_after: Whether to log memory after operation

    Returns:
        Dictionary with current memory size information
    """
    size_info = get_session_state_size(session_state)

    if log_before:
        logger.debug(
            f"[{operation_name}] Memory before: {size_info['total_size_mb']} MB"
        )

    if log_after:
        logger.debug(
            f"[{operation_name}] Memory after: {size_info['total_size_mb']} MB"
        )

    return size_info
