import io
import runpy
from types import SimpleNamespace
from typing import Any, Dict, List

import pandas as pd
import pytest
import streamlit as st


class DummyContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def markdown(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def success(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass

    def caption(self, *args, **kwargs):
        pass

    def text(self, *args, **kwargs):
        pass


class DummySpinner:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyForm(DummyContainer):
    def __init__(self, button_states: Dict[str, bool]):
        super().__init__()
        self._button_states = button_states

    def form_submit_button(self, label: str):
        return self._button_states.get(label, False)


class StubSessionState(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def stub_streamlit(monkeypatch):
    button_states: Dict[str, bool] = {}
    text_area_values: Dict[str, str] = {}
    text_input_values: Dict[str, str] = {}
    selectbox_choices: Dict[str, Any] = {}
    checkbox_states: Dict[str, bool] = {}
    uploader_value: Any = None

    session_state: StubSessionState = StubSessionState()
    secrets: Dict[str, Any] = {}

    def set_button(label: str, value: bool) -> None:
        button_states[label] = value

    def set_text_area(label: str, value: str) -> None:
        text_area_values[label] = value

    def set_text_input(label: str, value: str) -> None:
        text_input_values[label] = value

    def set_selectbox(label: str, value: Any) -> None:
        selectbox_choices[label] = value

    def set_checkbox(label: str, value: bool) -> None:
        checkbox_states[label] = value

    def set_uploader(value: Any) -> None:
        nonlocal uploader_value
        uploader_value = value

    monkeypatch.setattr(st, "session_state", session_state, raising=False)
    monkeypatch.setattr(st, "secrets", secrets, raising=False)

    monkeypatch.setattr(st, "set_page_config", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "title", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "subheader", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "header", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "markdown", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "divider", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "table", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "info", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "warning", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "success", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "error", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "write", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "caption", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "audio", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "download_button", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "toast", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "switch_page", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(st, "rerun", lambda *args, **kwargs: None, raising=False)

    def selectbox(label: str, options: List[Any], **kwargs) -> Any:
        if not options:
            return None
        return selectbox_choices.get(label, options[0])

    def text_area(label: str, value: str = "", **kwargs) -> str:
        return text_area_values.get(label, value)

    def text_input(label: str, value: str = "", **kwargs) -> str:
        return text_input_values.get(label, value)

    def checkbox(label: str, value: bool = False, **kwargs) -> bool:
        return checkbox_states.get(label, value)

    def button(label: str, **kwargs) -> bool:
        return button_states.get(label, False)

    def file_uploader(*args, **kwargs):
        return uploader_value

    monkeypatch.setattr(st, "selectbox", selectbox, raising=False)
    monkeypatch.setattr(st, "text_area", text_area, raising=False)
    monkeypatch.setattr(st, "text_input", text_input, raising=False)
    monkeypatch.setattr(st, "checkbox", checkbox, raising=False)
    monkeypatch.setattr(st, "button", button, raising=False)
    monkeypatch.setattr(st, "file_uploader", file_uploader, raising=False)
    monkeypatch.setattr(st, "slider", lambda *args, **kwargs: kwargs.get("value", 0.5), raising=False)

    monkeypatch.setattr(
        st,
        "columns",
        lambda layout: [DummyContainer() for _ in (layout if isinstance(layout, (list, tuple)) else range(layout))],
        raising=False,
    )
    monkeypatch.setattr(st, "expander", lambda *args, **kwargs: DummyContainer(), raising=False)
    monkeypatch.setattr(st, "spinner", lambda *args, **kwargs: DummySpinner(), raising=False)
    monkeypatch.setattr(st, "form", lambda *args, **kwargs: DummyForm(button_states), raising=False)
    monkeypatch.setattr(
        st,
        "form_submit_button",
        lambda label, **kwargs: button_states.get(label, False),
        raising=False,
    )

    def stop():
        raise RuntimeError("st.stop called")

    monkeypatch.setattr(st, "stop", stop, raising=False)

    return {
        "session_state": session_state,
        "secrets": secrets,
        "set_button": set_button,
        "set_text_area": set_text_area,
        "set_text_input": set_text_input,
        "set_selectbox": set_selectbox,
        "set_checkbox": set_checkbox,
        "set_uploader": set_uploader,
    }


@pytest.mark.core_suite
def test_app_page_generates_audio(monkeypatch, stub_streamlit, tmp_path):
    calls = {"generate_audio": 0}

    single_dir = tmp_path / "single"
    single_dir.mkdir()

    def fake_generate_audio(*args, **kwargs):
        calls["generate_audio"] += 1
        return True

    stub_streamlit["set_text_area"]("Text to speech", "Hello {name}")
    stub_streamlit["set_selectbox"]("Select model", "Model 1")
    stub_streamlit["set_selectbox"]("Select voice", "Voice 1")
    stub_streamlit["set_button"]("Generate Audio", True)
    stub_streamlit["session_state"]["ELEVENLABS_API_KEY"] = "sk-test"

    monkeypatch.setattr("utils.api_keys.get_elevenlabs_api_key", lambda: "sk-test")
    monkeypatch.setattr("utils.error_handling.validate_api_key", lambda *args, **kwargs: None)
    class ProgressStub:
        def __init__(self, *args, **kwargs):
            pass

        def update(self, *args, **kwargs):
            pass

        def complete(self, *args, **kwargs):
            pass

    monkeypatch.setattr("utils.error_handling.ProgressManager", ProgressStub)
    monkeypatch.setattr("utils.caching.Cache", lambda *args, **kwargs: SimpleNamespace(cleanup_expired=lambda: 0))
    monkeypatch.setattr("utils.session_manager.cleanup_old_sessions", lambda: None)
    monkeypatch.setattr("utils.session_manager.get_session_single_dir", lambda: str(single_dir))
    monkeypatch.setattr("scripts.Elevenlabs_functions.fetch_models", lambda *_: [("model-1", "Model 1")])
    monkeypatch.setattr("scripts.Elevenlabs_functions.fetch_voices", lambda *_: [("voice-1", "Voice 1")])
    monkeypatch.setattr("scripts.Elevenlabs_functions.get_voice_id", lambda *_: "voice-1")
    monkeypatch.setattr("scripts.Elevenlabs_functions.generate_audio", fake_generate_audio)
    monkeypatch.setattr(
        "scripts.openrouter_functions.get_default_enhancement_model",
        lambda: "openrouter/auto",
    )
    monkeypatch.setattr(
        "scripts.openrouter_functions.enhance_script_with_openrouter",
        lambda *args, **kwargs: (False, "Skipped"),
    )
    monkeypatch.setattr(
        "scripts.openrouter_functions.convert_word_to_phonetic_openrouter",
        lambda **kwargs: "phonetic",
    )
    stub_streamlit["session_state"]["models"] = [("model-1", "Model 1")]
    stub_streamlit["session_state"]["voices"] = [("voice-1", "Voice 1")]

    try:
        runpy.run_path("app.py", run_name="__main__")
    except RuntimeError as exc:
        if "st.stop" not in str(exc):
            raise

    assert calls["generate_audio"] == 1


@pytest.mark.core_suite
def test_bulk_generation_page_invokes_bulk_generation(monkeypatch, stub_streamlit):
    csv_bytes = io.BytesIO(b"text,filename\nHello {name},greeting_{name}")
    uploaded = SimpleNamespace(
        name="demo.csv",
        size=len(csv_bytes.getvalue()),
        read=csv_bytes.read,
        seek=csv_bytes.seek,
    )
    stub_streamlit["set_uploader"](uploaded)
    stub_streamlit["set_button"]("Generate Bulk Audio", True)
    stub_streamlit["set_selectbox"]("Select model", "Model 1")
    stub_streamlit["set_selectbox"]("Select voice", "Voice 1")
    df = pd.DataFrame([{"text": "Hello {name}", "filename": "greeting_{name}", "name": "Alice"}])
    monkeypatch.setattr("pandas.read_csv", lambda *_: df.copy())

    success_messages: List[str] = []

    def record_bulk(*args, **kwargs):
        return True, "ok"

    from pages import Bulk_Generation
    monkeypatch.setattr(Bulk_Generation, "get_elevenlabs_api_key", lambda: "sk-test")
    monkeypatch.setattr(Bulk_Generation, "validate_api_key", lambda *args, **kwargs: None)
    monkeypatch.setattr(Bulk_Generation, "cleanup_old_sessions", lambda: None)
    monkeypatch.setattr(Bulk_Generation, "get_session_bulk_dir", lambda name: f"outputs/{name}")
    monkeypatch.setattr(Bulk_Generation, "fetch_models", lambda *_: [("model-1", "Model 1")])
    monkeypatch.setattr(Bulk_Generation, "fetch_voices", lambda *_: [("voice-1", "Voice 1")])
    monkeypatch.setattr(Bulk_Generation, "get_voice_id", lambda *_: "voice-1")
    monkeypatch.setattr(Bulk_Generation, "supports_speed", lambda *_: False)
    monkeypatch.setattr(Bulk_Generation, "validate_csv_file_size", lambda *_: True)
    monkeypatch.setattr(Bulk_Generation, "validate_dataframe_rows", lambda *_: True)
    monkeypatch.setattr(Bulk_Generation, "validate_column_name", lambda *_: True)
    monkeypatch.setattr(Bulk_Generation, "sanitize_path_component", lambda name: name)
    monkeypatch.setattr(Bulk_Generation, "validate_path_within_base", lambda *args, **kwargs: True)
    monkeypatch.setattr(Bulk_Generation, "bulk_generate_audio", record_bulk)
    monkeypatch.setattr(st, "stop", lambda: None, raising=False)
    monkeypatch.setattr(st, "success", lambda message: success_messages.append(message), raising=False)

    Bulk_Generation.main()
    assert any("Bulk generation completed!" in message for message in success_messages)


@pytest.mark.core_suite
def test_translation_page_triggers_translation(monkeypatch, stub_streamlit):
    calls = {"translate": 0}

    stub_streamlit["set_text_area"]("Enter text to translate", "Hello there")
    stub_streamlit["set_selectbox"]("Select target language", "French")
    stub_streamlit["set_button"]("Translate", True)

    monkeypatch.setattr("scripts.openrouter_functions.get_openrouter_api_key", lambda: "sk-open")
    monkeypatch.setattr("scripts.openrouter_functions.fetch_openrouter_models", lambda: [{"id": "model-1", "name": "Model 1", "pricing": {"prompt": 0, "completion": 0}}])
    monkeypatch.setattr("scripts.openrouter_functions.filter_free_models", lambda models, show_free_only=True: models)
    monkeypatch.setattr("scripts.openrouter_functions.search_models_fuzzy", lambda models, query: models)
    monkeypatch.setattr("scripts.openrouter_functions.get_default_translation_model", lambda: "model-1")
    monkeypatch.setattr("utils.security.validate_text_length", lambda *_: True)
    monkeypatch.setattr(
        "scripts.Translation_functions.translate_script",
        lambda *args, **kwargs: calls.update(translate=calls["translate"] + 1) or "Bonjour",
    )
    monkeypatch.setattr("utils.error_handling.handle_error", lambda *args, **kwargs: (False, "handled"))

    try:
        runpy.run_path("pages/3_Translation.py", run_name="__main__")
    except RuntimeError as exc:
        if "st.stop" not in str(exc):
            raise

    assert calls["translate"] == 1


@pytest.mark.core_suite
def test_settings_page_updates_session_state(monkeypatch, stub_streamlit):
    stub_streamlit["set_text_input"]("ElevenLabs API Key", "eleven-key")
    stub_streamlit["set_text_input"]("OpenRouter API Key", "openrouter-key")
    stub_streamlit["set_button"]("Save API Keys", True)
    stub_streamlit["session_state"]["default_translation_model"] = "model-1"
    stub_streamlit["session_state"]["default_enhancement_model"] = "model-1"

    monkeypatch.setattr("scripts.openrouter_functions.get_openrouter_api_key", lambda: "sk-open")
    monkeypatch.setattr("scripts.openrouter_functions.fetch_openrouter_models", lambda: [{"id": "model-1", "name": "Model 1", "pricing": {"prompt": 0, "completion": 0}}])
    monkeypatch.setattr("scripts.openrouter_functions.filter_free_models", lambda models, show_free_only=True: models)
    monkeypatch.setattr("scripts.openrouter_functions.search_models_fuzzy", lambda models, query: models)
    monkeypatch.setattr("utils.error_handling.validate_api_key", lambda *args, **kwargs: None)
    monkeypatch.setattr("utils.error_handling.handle_error", lambda *args, **kwargs: (False, "handled"))

    from pages import Settings

    try:
        Settings.main()
    except RuntimeError as exc:
        if "st.stop" not in str(exc):
            raise

    assert stub_streamlit["session_state"].get("ELEVENLABS_API_KEY") == "eleven-key"
    assert stub_streamlit["session_state"].get("OPENROUTER_API_KEY") == "openrouter-key"


@pytest.mark.core_suite
def test_file_explorer_page_lists_outputs(monkeypatch, stub_streamlit, tmp_path):
    session_dir = tmp_path / "outputs"
    bulk_dir = session_dir / "bulk" / "demo"
    single_dir = session_dir / "single"
    bulk_dir.mkdir(parents=True)
    single_dir.mkdir(parents=True)

    bulk_file = bulk_dir / "demo_file.mp3"
    bulk_file.write_bytes(b"binary")
    single_file = single_dir / "en_voice_20250101_abc12345.mp3"
    single_file.write_bytes(b"binary")

    monkeypatch.setattr("utils.session_manager.cleanup_old_sessions", lambda: None)
    monkeypatch.setattr("utils.session_manager.get_session_id", lambda: "abcdef123456")
    monkeypatch.setattr("utils.session_manager.get_session_output_dir", lambda: str(session_dir))
    monkeypatch.setattr("utils.security.validate_path_within_base", lambda *args, **kwargs: True)
    monkeypatch.setattr("utils.security.escape_html_content", lambda value: value)
    monkeypatch.setattr("os.path.exists", lambda path: True)
    monkeypatch.setattr(
        "os.listdir",
        lambda path: ["demo"] if path.endswith("bulk") else ["demo_file.mp3"] if path.endswith("demo") else ["en_voice_20250101_abc12345.mp3"],
    )
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.BytesIO(b"binary"), raising=False)

    try:
        runpy.run_path("pages/File_Explorer.py", run_name="__main__")
    except RuntimeError as exc:
        if "st.stop" not in str(exc):
            raise

    # ensure session state not modified unexpectedly
    assert "generated_audio" not in stub_streamlit["session_state"]


@pytest.mark.core_suite
def test_voice_design_workflow_uses_api_functions(monkeypatch, stub_streamlit):
    calls = {"previews": 0, "create": 0}

    def fake_generate_previews(*args, **kwargs):
        calls["previews"] += 1
        return {"generated_voice_id": "voice-xyz", "audio": [{"id": "preview-1", "path": "preview_0.mp3"}]}

    def fake_create_voice(*args, **kwargs):
        calls["create"] += 1
        return {"status": "ok"}

    stub_streamlit["set_text_area"]("Voice description", "Warm narrator")
    stub_streamlit["set_button"]("Generate Previews", True)
    stub_streamlit["set_button"]("Create Voice", True)
    stub_streamlit["set_text_input"]("Voice name", "Narrator Voice")

    monkeypatch.setattr("scripts.Elevenlabs_functions.generate_voice_previews", fake_generate_previews)
    monkeypatch.setattr("scripts.Elevenlabs_functions.create_voice_from_preview", fake_create_voice)

    def voice_design_demo():
        st.title("Voice Design")
        description = st.text_area("Voice description")
        if st.button("Generate Previews") and description:
            previews = fake_generate_previews("sk", description)
            st.session_state["voice_preview"] = previews["generated_voice_id"]
        if st.button("Create Voice") and st.session_state.get("voice_preview"):
            name = st.text_input("Voice name")
            if name:
                fake_create_voice("sk", name, description, st.session_state["voice_preview"])
                st.success("Voice created")

    try:
        voice_design_demo()
    except RuntimeError as exc:
        if "st.stop" not in str(exc):
            raise

    assert calls["previews"] == 1
    assert calls["create"] == 1

