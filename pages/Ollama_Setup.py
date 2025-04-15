import streamlit as st
import subprocess
import re
import shutil

# Apply custom styling
try:
    with open("custom_style.css", encoding="utf-8") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

st.title("Ollama Setup & Onboarding")
st.markdown(
    """
Welcome to ElevenTools! Before you begin, let's set up your Large Language Model (LLM) preferences.

**Ollama** is the default LLM engine used for script enhancement and phonetic conversion. You can select your preferred model below. This choice will affect how scripts are processed throughout the app.
"""
)


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
    st.error("Ollama is not installed on your system.")
    st.markdown(
        """
### Installation Instructions

1. **Install Ollama:**
   - macOS: `brew install ollama`
   - Linux: [See instructions](https://ollama.com/download)
   - Windows: [See instructions](https://ollama.com/download)

2. **Pull recommended models:**
   - `ollama pull llama3.2:3b`  
   - `ollama pull llama3.2:1b-instruct-fp16`  

These models are small, fast, and suitable for most use cases in ElevenTools.

After installation, restart the app and return to this page.
"""
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
    "Select your preferred LLM model:",
    options=model_names,
    index=0,
    help="Choose from your locally installed Ollama models.",
)

selected_model_id = AVAILABLE_MODELS[model_names.index(selected_model_name)]["id"]

# Save selection in session state
st.session_state["ollama_model_id"] = selected_model_id

st.info(f"You have selected: **{selected_model_name}**")

# Confirm setup
if st.button("Finish Setup"):
    st.session_state["ollama_setup_complete"] = True
    st.success("Ollama setup complete! You can now access all features.")
    st.balloons()

if not st.session_state.get("ollama_setup_complete", False):
    st.warning("Please complete the Ollama setup before using other features.")
    st.stop()
