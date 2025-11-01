import pytest
from unittest.mock import patch, MagicMock
import builtins


# Patch Streamlit and os modules for isolated testing
def test_outputs_dir_missing(monkeypatch):
    # Simulate outputs directory missing
    with (
        patch("os.path.exists", return_value=False),
        patch("os.listdir", return_value=[]),  # Patch to prevent FileNotFoundError
        patch("streamlit.info") as mock_info,
        patch("streamlit.stop") as mock_stop,
    ):
        import importlib
        import pages.File_Explorer as file_explorer

        importlib.reload(file_explorer)
        # Check that info was called at least once with the expected message
        expected_msg = (
            "No generated audio found. The 'outputs' directory does not exist yet."
        )
        assert mock_info.call_count >= 1
        mock_info.assert_any_call(expected_msg)
        mock_stop.assert_called()


def test_empty_outputs(monkeypatch):
    # Simulate outputs directory exists but is empty
    with (
        patch("os.path.exists", side_effect=lambda p: True),
        patch("os.listdir", return_value=[]),
        patch("streamlit.header") as mock_header,
        patch("streamlit.write") as mock_write,
    ):
        import importlib
        import pages.File_Explorer as file_explorer

        importlib.reload(file_explorer)
        # Should call header for both sections at least once
        assert mock_header.call_count >= 2  # At least for Bulk and Single Outputs
        assert any(
            "No bulk outputs found." in str(call) for call in mock_write.call_args_list
        )
        assert any(
            "No single outputs found." in str(call)
            for call in mock_write.call_args_list
        )


def test_bulk_and_single_outputs(monkeypatch):
    # Simulate outputs directory with one bulk group and one single file
    def fake_listdir(path):
        if path.endswith("outputs"):
            return ["bulk_csv", "single"]
        elif path.endswith("outputs/bulk_csv"):
            return ["audio1.mp3"]
        elif path.endswith("outputs/single"):
            return ["en_VoiceA_20240101_abc12345.mp3"]  # Format: lang_voice_date_id.mp3
        return []

    def fake_isdir(path):
        return path.endswith("outputs/bulk_csv") or path.endswith("outputs/single")

    # Patch Streamlit functions BEFORE importing the module
    with (
        patch("streamlit.title"),
        patch("streamlit.info"),
        patch("streamlit.stop"),
        patch("os.path.exists", return_value=True),
        patch("os.listdir", side_effect=fake_listdir),
        patch("os.path.isdir", side_effect=fake_isdir),
        patch("streamlit.header") as mock_header,
        patch("streamlit.expander") as mock_expander,
        patch("streamlit.audio") as mock_audio,
        patch("streamlit.write") as mock_write,
        patch("streamlit.columns") as mock_columns,
    ):
        # Mock columns to return a context manager
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_columns.return_value = (mock_col1, mock_col2)
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        
        import importlib
        import pages.File_Explorer as file_explorer

        importlib.reload(file_explorer)
        # Check that expanders and audio players are called
        assert mock_expander.call_count >= 1  # At least one bulk group
        assert mock_audio.call_count >= 2  # At least one bulk, one single (may be more due to reload)
        # Check that metadata is written
        # Get all write call arguments (st.write() is called with positional args)
        write_calls = [str(call[0][0]) if call[0] and len(call[0]) > 0 else "" for call in mock_write.call_args_list]
        # Check for metadata (may include markdown formatting)
        assert any("Filename" in call or "filename" in call.lower() for call in write_calls)
        assert any("Source CSV" in call or "source csv" in call.lower() for call in write_calls)
        # Language and Voice are only written for single files with parsed metadata
        assert any("Language" in call or "language" in call.lower() for call in write_calls)
        assert any("Voice" in call or "voice" in call.lower() for call in write_calls)
