import pytest
import streamlit as st

from utils import api_keys, error_handling, model_capabilities


@pytest.fixture(autouse=True)
def clear_session_state():
    st.session_state.clear()
    yield
    st.session_state.clear()


@pytest.mark.core_suite
def test_api_key_retrieval_from_session_and_secrets(monkeypatch):
    monkeypatch.setattr(
        st,
        "secrets",
        {"ELEVENLABS_API_KEY": "fallback", "OPENROUTER_API_KEY": "fallback-openrouter"},
        raising=False,
    )
    st.session_state["ELEVENLABS_API_KEY"] = "session-key"

    assert api_keys.get_elevenlabs_api_key() == "session-key"
    assert api_keys.get_openrouter_api_key() == "fallback-openrouter"


@pytest.mark.core_suite
def test_validate_api_key_guardrails():
    with pytest.raises(error_handling.ConfigurationError):
        error_handling.validate_api_key(None, "ElevenLabs")

    with pytest.raises(error_handling.ConfigurationError):
        error_handling.validate_api_key("sk-dummy-test", "ElevenLabs")


@pytest.mark.core_suite
def test_handle_error_routes_messages(mocker):
    error_placeholder = mocker.Mock()
    warn_placeholder = mocker.Mock()
    info_placeholder = mocker.Mock()

    mocker.patch("streamlit.error", error_placeholder)
    mocker.patch("streamlit.warning", warn_placeholder)
    mocker.patch("streamlit.info", info_placeholder)

    err = error_handling.APIError("Failure", "Details here")
    success, message = error_handling.handle_error(err)

    assert success is False
    assert message == "Failure (Details: Details here)"
    assert any(
        call.args and call.args[0] == "🔌 API Error: Failure"
        for call in error_placeholder.call_args_list
    )
    assert not info_placeholder.called


@pytest.mark.core_suite
def test_progress_manager_updates_status(mocker):
    progress_mock = mocker.Mock()
    status_mock = mocker.Mock()
    mocker.patch("streamlit.progress", return_value=progress_mock)
    mocker.patch("streamlit.empty", return_value=status_mock)

    manager = error_handling.ProgressManager(total_steps=4)
    manager.update(2, "Working")
    progress_mock.progress.assert_called_with(0.5)
    status_mock.text.assert_called_with("Working (50%)")

    manager.complete(success=True)
    status_mock.success.assert_called()
    progress_mock.progress.assert_called_with(1.0)


@pytest.mark.core_suite
def test_model_capabilities_summary():
    capabilities = model_capabilities.get_model_capabilities("eleven_multilingual_v2")
    assert capabilities["speed"] is True
    assert capabilities["audio_tags"] is False

    capabilities_v3 = model_capabilities.get_model_capabilities("eleven_v3")
    assert capabilities_v3["audio_tags"] is True

