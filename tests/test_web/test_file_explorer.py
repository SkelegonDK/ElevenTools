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
            return ["en_VoiceA_20240101_abc12345_12345.mp3"]
        return []

    def fake_isdir(path):
        return path.endswith("outputs/bulk_csv") or path.endswith("outputs/single")

    with (
        patch("os.path.exists", return_value=True),
        patch("os.listdir", side_effect=fake_listdir),
        patch("os.path.isdir", side_effect=fake_isdir),
        patch("streamlit.header") as mock_header,
        patch("streamlit.expander") as mock_expander,
        patch("streamlit.audio") as mock_audio,
        patch("streamlit.write") as mock_write,
    ):
        import importlib
        import pages.File_Explorer as file_explorer

        importlib.reload(file_explorer)
        # Check that expanders and audio players are called
        assert mock_expander.call_count == 1  # One bulk group
        assert mock_audio.call_count == 2  # One bulk, one single
        # Check that metadata is written
        assert any("Filename:" in str(call) for call in mock_write.call_args_list)
        assert any("Source CSV:" in str(call) for call in mock_write.call_args_list)
        assert any("Language:" in str(call) for call in mock_write.call_args_list)
        assert any("Voice:" in str(call) for call in mock_write.call_args_list)
