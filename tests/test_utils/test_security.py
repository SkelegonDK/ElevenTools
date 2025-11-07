"""Tests for security utilities."""

import pytest
import os
from utils.security import (
    sanitize_path_component,
    validate_path_within_base,
    validate_csv_file_size,
    validate_dataframe_rows,
    validate_column_name,
    validate_text_length,
    escape_html_content,
    sanitize_filename,
    MAX_CSV_SIZE,
    MAX_DF_ROWS,
    MAX_TEXT_LENGTH,
)


class TestSanitizePathComponent:
    """Tests for path component sanitization."""

    def test_sanitize_normal_filename(self):
        """Test sanitization of normal filename."""
        result = sanitize_path_component("my_file.csv")
        assert result == "my_file.csv"

    def test_sanitize_path_traversal(self):
        """Test sanitization prevents path traversal."""
        result = sanitize_path_component("../../../etc/passwd")
        assert "../" not in result
        assert "etc_passwd" in result

    def test_sanitize_dangerous_characters(self):
        """Test sanitization removes dangerous characters."""
        result = sanitize_path_component("file<>name|with*chars")
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert "*" not in result

    def test_sanitize_empty_string(self):
        """Test sanitization of empty string."""
        result = sanitize_path_component("")
        assert result == "default"

    def test_sanitize_dots_only(self):
        """Test sanitization of dots-only string."""
        result = sanitize_path_component("..")
        assert result == "default"

    def test_sanitize_length_limit(self):
        """Test sanitization respects length limit."""
        long_string = "a" * 200
        result = sanitize_path_component(long_string, max_length=100)
        assert len(result) <= 100


class TestValidatePathWithinBase:
    """Tests for path validation."""

    def test_valid_path_within_base(self, tmp_path):
        """Test valid path within base directory."""
        base_dir = str(tmp_path / "base")
        os.makedirs(base_dir, exist_ok=True)
        test_path = str(tmp_path / "base" / "subdir" / "file.txt")
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        
        assert validate_path_within_base(test_path, base_dir) is True

    def test_invalid_path_outside_base(self, tmp_path):
        """Test invalid path outside base directory."""
        base_dir = str(tmp_path / "base")
        os.makedirs(base_dir, exist_ok=True)
        test_path = str(tmp_path / "other" / "file.txt")
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        
        assert validate_path_within_base(test_path, base_dir) is False

    def test_absolute_paths(self, tmp_path):
        """Test validation with absolute paths."""
        base_dir = str(tmp_path / "base")
        os.makedirs(base_dir, exist_ok=True)
        test_path = str(tmp_path / "base" / "file.txt")
        
        abs_base = os.path.abspath(base_dir)
        abs_path = os.path.abspath(test_path)
        
        assert validate_path_within_base(abs_path, abs_base) is True


class TestValidateCsvFileSize:
    """Tests for CSV file size validation."""

    def test_valid_file_size(self):
        """Test validation of valid file size."""
        assert validate_csv_file_size(5 * 1024 * 1024) is True  # 5MB

    def test_file_size_at_limit(self):
        """Test validation at size limit."""
        assert validate_csv_file_size(MAX_CSV_SIZE) is True

    def test_file_size_exceeds_limit(self):
        """Test validation rejects oversized files."""
        assert validate_csv_file_size(MAX_CSV_SIZE + 1) is False

    def test_custom_limit(self):
        """Test validation with custom limit."""
        assert validate_csv_file_size(1000, max_size=2000) is True
        assert validate_csv_file_size(3000, max_size=2000) is False


class TestValidateDataframeRows:
    """Tests for DataFrame row validation."""

    def test_valid_row_count(self):
        """Test validation of valid row count."""
        assert validate_dataframe_rows(500) is True

    def test_row_count_at_limit(self):
        """Test validation at row limit."""
        assert validate_dataframe_rows(MAX_DF_ROWS) is True

    def test_row_count_exceeds_limit(self):
        """Test validation rejects excessive rows."""
        assert validate_dataframe_rows(MAX_DF_ROWS + 1) is False

    def test_custom_limit(self):
        """Test validation with custom limit."""
        assert validate_dataframe_rows(50, max_rows=100) is True
        assert validate_dataframe_rows(150, max_rows=100) is False


class TestValidateColumnName:
    """Tests for column name validation."""

    def test_valid_column_name(self):
        """Test validation of valid column names."""
        assert validate_column_name("text") is True
        assert validate_column_name("filename") is True
        assert validate_column_name("user_name") is True
        assert validate_column_name("col123") is True

    def test_invalid_column_name(self):
        """Test validation rejects invalid column names."""
        assert validate_column_name("col-name") is False  # hyphen
        assert validate_column_name("col.name") is False  # dot
        assert validate_column_name("col name") is False  # space
        assert validate_column_name("col/name") is False  # slash
        assert validate_column_name("") is False  # empty

    def test_special_characters(self):
        """Test validation rejects special characters."""
        assert validate_column_name("col@name") is False
        assert validate_column_name("col#name") is False
        assert validate_column_name("col$name") is False


class TestValidateTextLength:
    """Tests for text length validation."""

    def test_valid_text_length(self):
        """Test validation of valid text length."""
        assert validate_text_length("Short text") is True
        assert validate_text_length("a" * 1000) is True

    def test_text_at_limit(self):
        """Test validation at text length limit."""
        assert validate_text_length("a" * MAX_TEXT_LENGTH) is True

    def test_text_exceeds_limit(self):
        """Test validation rejects overly long text."""
        assert validate_text_length("a" * (MAX_TEXT_LENGTH + 1)) is False

    def test_custom_limit(self):
        """Test validation with custom limit."""
        assert validate_text_length("short", max_length=100) is True
        assert validate_text_length("a" * 150, max_length=100) is False


class TestEscapeHtmlContent:
    """Tests for HTML content escaping."""

    def test_escape_html_tags(self):
        """Test escaping of HTML tags."""
        result = escape_html_content("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_escape_special_characters(self):
        """Test escaping of special HTML characters."""
        result = escape_html_content("Text & More")
        assert "&amp;" in result

    def test_escape_quotes(self):
        """Test escaping of quotes."""
        result = escape_html_content('Text "quoted"')
        assert "&quot;" in result

    def test_normal_text_unchanged(self):
        """Test normal text is not modified."""
        text = "Normal text without special characters"
        result = escape_html_content(text)
        assert result == text


class TestSanitizeFilename:
    """Tests for filename sanitization."""

    def test_sanitize_normal_filename(self):
        """Test sanitization of normal filename."""
        result = sanitize_filename("my_file.mp3")
        assert result == "my_file.mp3"

    def test_sanitize_dangerous_characters(self):
        """Test sanitization removes dangerous characters."""
        result = sanitize_filename("file<>name|with*chars.mp3")
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert "*" not in result
        assert result.endswith(".mp3")

    def test_sanitize_preserves_extension(self):
        """Test sanitization preserves file extension."""
        result = sanitize_filename("file.name.mp3")
        assert result.endswith(".mp3")

    def test_sanitize_length_limit(self):
        """Test sanitization respects length limit."""
        long_name = "a" * 200 + ".mp3"
        result = sanitize_filename(long_name, max_length=100)
        assert len(result) <= 100
        assert result.endswith(".mp3")

    def test_sanitize_empty_string(self):
        """Test sanitization of empty string."""
        result = sanitize_filename("")
        assert result == "default"

