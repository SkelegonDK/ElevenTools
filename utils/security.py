"""Security utilities for ElevenTools.

This module provides security functions for path sanitization, input validation,
and content escaping to prevent common security vulnerabilities.
"""

import html
import os
import re

# Security limits
MAX_CSV_SIZE = 10 * 1024 * 1024  # 10MB
MAX_DF_ROWS = 1000
MAX_TEXT_LENGTH = 10000
MAX_FILENAME_LENGTH = 100


def sanitize_path_component(
    component: str, max_length: int = MAX_FILENAME_LENGTH
) -> str:
    """Sanitize a path component to prevent directory traversal attacks.

    Removes path separators, dangerous characters, and limits length.
    Ensures the component cannot be used for path traversal.

    Args:
        component: The path component to sanitize (e.g., filename, directory name)
        max_length: Maximum length for the sanitized component (default: 100)

    Returns:
        Sanitized path component safe for use in file paths

    Example:
        >>> sanitize_path_component("../../../etc/passwd")
        'etc_passwd'
        >>> sanitize_path_component("my_file.csv")
        'my_file.csv'
    """
    if not component:
        return "default"

    # Remove path separators and dangerous characters
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", str(component))

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Limit length
    sanitized = sanitized[:max_length]

    # Ensure not empty or just dots (which could be traversal)
    if not sanitized or sanitized in (".", ".."):
        sanitized = "default"

    return sanitized


def validate_path_within_base(path: str, base_dir: str) -> bool:
    """Validate that a path remains within a base directory.

    Prevents directory traversal attacks by ensuring the resolved path
    is within the intended base directory.

    Args:
        path: The path to validate
        base_dir: The base directory that the path must remain within

    Returns:
        True if path is safe (within base_dir), False otherwise
    """
    try:
        # Resolve both paths to absolute paths
        abs_path = os.path.abspath(path)
        abs_base = os.path.abspath(base_dir)

        # Check if the resolved path starts with the base directory
        return abs_path.startswith(abs_base)
    except Exception:
        return False


def validate_csv_file_size(file_size: int, max_size: int = MAX_CSV_SIZE) -> bool:
    """Validate CSV file size against maximum limit.

    Args:
        file_size: Size of the CSV file in bytes
        max_size: Maximum allowed size in bytes (default: 10MB)

    Returns:
        True if file size is within limit, False otherwise
    """
    return file_size <= max_size


def validate_dataframe_rows(num_rows: int, max_rows: int = MAX_DF_ROWS) -> bool:
    """Validate DataFrame row count against maximum limit.

    Args:
        num_rows: Number of rows in the DataFrame
        max_rows: Maximum allowed rows (default: 1000)

    Returns:
        True if row count is within limit, False otherwise
    """
    return num_rows <= max_rows


def validate_column_name(column_name: str) -> bool:
    """Validate CSV column name format.

    Column names must contain only alphanumeric characters and underscores.

    Args:
        column_name: The column name to validate

    Returns:
        True if column name is valid, False otherwise
    """
    if not column_name:
        return False

    # Allow only alphanumeric characters and underscores
    pattern = r"^[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, column_name))


def validate_text_length(text: str, max_length: int = MAX_TEXT_LENGTH) -> bool:
    """Validate text input length against maximum limit.

    Args:
        text: The text to validate
        max_length: Maximum allowed length in characters (default: 10000)

    Returns:
        True if text length is within limit, False otherwise
    """
    return len(text) <= max_length


def escape_html_content(content: str) -> str:
    """Escape HTML special characters to prevent XSS attacks.

    Args:
        content: The content to escape

    Returns:
        Escaped content safe for HTML rendering
    """
    return html.escape(str(content))


def sanitize_filename(filename: str, max_length: int = MAX_FILENAME_LENGTH) -> str:
    """Sanitize a filename for safe file system use.

    Removes dangerous characters and limits length, similar to
    sanitize_path_component but preserves common filename characters.

    Args:
        filename: The filename to sanitize
        max_length: Maximum length for the filename (default: 100)

    Returns:
        Sanitized filename safe for file system use
    """
    if not filename:
        return "default"

    # Remove path separators and dangerous characters
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", str(filename))

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Limit length (preserve extension if present)
    if "." in sanitized:
        name, ext = os.path.splitext(sanitized)
        name = name[: max_length - len(ext)]
        sanitized = name + ext
    else:
        sanitized = sanitized[:max_length]

    # Ensure not empty
    if not sanitized or sanitized in (".", ".."):
        sanitized = "default"

    return sanitized
