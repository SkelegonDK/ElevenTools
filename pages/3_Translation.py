import streamlit as st
import subprocess
import re
import shutil
from scripts.Translation_functions import translate_script

with open("custom_style.css", encoding="utf-8") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

st.title("Script Translation")


def is_ollama_installed():
    return shutil.which("ollama") is not None


def get_local_ollama_models():
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        models = []
        for line in lines[1:]:  # Skip header
            match = re.match(r"^(\S+)\s+(\S+)\s+([\d.]+\s+\w+)\s+(.+)$", line)
            if match:
                name, model_id, size, modified = match.groups()
                models.append(
                    {"id": name, "name": name, "size": size, "modified": modified}
                )
        return models
    except Exception as e:
        st.error(f"Could not retrieve local Ollama models: {e}")
        return []


if not is_ollama_installed():
    st.error(
        "Ollama is not installed. Please install Ollama and at least one model to use translation features."
    )
    st.stop()

AVAILABLE_MODELS = get_local_ollama_models()
if not AVAILABLE_MODELS:
    st.warning(
        "No local Ollama models found. Please install a model using 'ollama pull llama3.2:3b' before proceeding."
    )
    st.stop()

model_names = [
    f"{model['name']} ({model['size']}, {model['modified']})"
    for model in AVAILABLE_MODELS
]
selected_model_name = st.selectbox(
    "Select LLM model for translation:",
    options=model_names,
    index=0,
    help="Choose from your locally installed Ollama models.",
)
selected_model_id = AVAILABLE_MODELS[model_names.index(selected_model_name)]["id"]
st.session_state["translation_ollama_model_id"] = selected_model_id

# Input text
text = st.text_area("Enter text to translate")

# Select language
language = st.selectbox(
    "Select target language",
    ["Spanish", "French", "German", "Italian", "Portuguese", "Dutch"],
)

# Generate translation
if st.button("Translate") and text:
    translation = translate_script(text, language)
    st.write("Translation:")
    st.write(translation)
