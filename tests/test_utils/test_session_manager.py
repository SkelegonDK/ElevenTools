"""Tests for session management utilities."""

import os
import time
from unittest.mock import patch

from utils.session_manager import (
    cleanup_old_sessions,
    get_session_bulk_dir,
    get_session_id,
    get_session_output_dir,
    get_session_single_dir,
)


class TestSessionID:
    """Tests for session ID generation."""

    def test_get_session_id_creates_new_id(self):
        """Test that get_session_id creates a new ID when none exists."""
        with patch("streamlit.session_state", {}):
            session_id = get_session_id()
            assert session_id is not None
            assert isinstance(session_id, str)
            assert len(session_id) > 0

    def test_get_session_id_returns_existing_id(self):
        """Test that get_session_id returns existing ID from session state."""
        existing_id = "test-session-id-123"
        with patch("streamlit.session_state", {"session_id": existing_id}):
            session_id = get_session_id()
            assert session_id == existing_id


class TestSessionDirectories:
    """Tests for session directory creation."""

    def test_get_session_output_dir_creates_directory(self, tmp_path):
        """Test that get_session_output_dir creates the directory."""
        with patch("os.getcwd", return_value=str(tmp_path)):
            with patch("streamlit.session_state", {}):
                output_dir = get_session_output_dir()
                assert os.path.exists(output_dir)
                assert os.path.isdir(output_dir)

    def test_get_session_single_dir_creates_directory(self, tmp_path):
        """Test that get_session_single_dir creates the directory."""
        with patch("os.getcwd", return_value=str(tmp_path)):
            with patch("streamlit.session_state", {}):
                single_dir = get_session_single_dir()
                assert os.path.exists(single_dir)
                assert os.path.isdir(single_dir)
                assert "single" in single_dir

    def test_get_session_bulk_dir_creates_directory(self, tmp_path):
        """Test that get_session_bulk_dir creates the directory."""
        with patch("os.getcwd", return_value=str(tmp_path)):
            with patch("streamlit.session_state", {}):
                bulk_dir = get_session_bulk_dir("test_csv")
                assert os.path.exists(bulk_dir)
                assert os.path.isdir(bulk_dir)
                assert "bulk" in bulk_dir
                assert "test_csv" in bulk_dir

    def test_session_directories_are_unique(self, tmp_path):
        """Test that different sessions get different directories."""
        with patch("os.getcwd", return_value=str(tmp_path)):
            with patch("streamlit.session_state", {}):
                dir1 = get_session_output_dir()
            with patch("streamlit.session_state", {}):
                dir2 = get_session_output_dir()
            assert dir1 != dir2


class TestCleanupOldSessions:
    """Tests for cleanup of old session directories."""

    def test_cleanup_removes_old_directories(self, tmp_path):
        """Test that cleanup removes directories older than threshold."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()

        # Create old session directory
        old_session = outputs_dir / "old-session-id"
        old_session.mkdir()
        old_file = old_session / "test.mp3"
        old_file.write_text("test")

        # Set modification time to 25 hours ago
        old_time = time.time() - (25 * 3600)
        os.utime(str(old_session), (old_time, old_time))

        with patch("os.getcwd", return_value=str(tmp_path)):
            removed = cleanup_old_sessions(max_age_hours=24)
            assert removed == 1
            assert not old_session.exists()

    def test_cleanup_preserves_recent_directories(self, tmp_path):
        """Test that cleanup preserves directories newer than threshold."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()

        # Create recent session directory
        recent_session = outputs_dir / "recent-session-id"
        recent_session.mkdir()
        recent_file = recent_session / "test.mp3"
        recent_file.write_text("test")

        # Set modification time to 1 hour ago
        recent_time = time.time() - (1 * 3600)
        os.utime(str(recent_session), (recent_time, recent_time))

        with patch("os.getcwd", return_value=str(tmp_path)):
            removed = cleanup_old_sessions(max_age_hours=24)
            assert removed == 0
            assert recent_session.exists()

    def test_cleanup_skips_non_session_directories(self, tmp_path):
        """Test that cleanup skips directories like 'single' and 'bulk'."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()

        # Create non-session directories
        single_dir = outputs_dir / "single"
        single_dir.mkdir()
        bulk_dir = outputs_dir / "bulk"
        bulk_dir.mkdir()

        # Create old session directory
        old_session = outputs_dir / "old-session-id"
        old_session.mkdir()
        old_time = time.time() - (25 * 3600)
        os.utime(str(old_session), (old_time, old_time))

        with patch("os.getcwd", return_value=str(tmp_path)):
            removed = cleanup_old_sessions(max_age_hours=24)
            assert removed == 1
            assert single_dir.exists()  # Should be preserved
            assert bulk_dir.exists()  # Should be preserved
            assert not old_session.exists()  # Should be removed

    def test_cleanup_handles_missing_outputs_dir(self, tmp_path):
        """Test that cleanup handles missing outputs directory gracefully."""
        outputs_dir = tmp_path / "outputs"
        # Don't create outputs directory

        with patch("os.getcwd", return_value=str(tmp_path)):
            removed = cleanup_old_sessions(max_age_hours=24)
            assert removed == 0

    def test_cleanup_handles_permission_errors(self, tmp_path):
        """Test that cleanup handles permission errors gracefully."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()

        # Create session directory
        session_dir = outputs_dir / "session-id"
        session_dir.mkdir()

        # Mock os.listdir to raise PermissionError
        with patch("os.getcwd", return_value=str(tmp_path)):
            with patch("os.listdir", side_effect=PermissionError("Access denied")):
                removed = cleanup_old_sessions(max_age_hours=24)
                # Should not raise exception, just return 0
                assert removed == 0
