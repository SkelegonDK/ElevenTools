import streamlit as st
from functions import detect_string_variables, detect_phonetic_conversion
from Elevenlabs_functions import (
    generate_audio,
    fetch_models,
    fetch_voices,
    get_voice_id,
)
from ollama_functions import enhance_script_with_ollama, convert_word_to_phonetic
import uuid
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="ElevenTools", page_icon="🔊", layout="centered")

# Initialize API keys
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
OPENAI_API = st.secrets["OPENAI_API_KEY"]

if ELEVENLABS_API_KEY is None:
    ELEVENLABS_API_KEY = "sk-dummy"
    st.warning("Elevenlabs API key not found. Using dummy key")

if OPENAI_API is None:
    OPENAI_API = "sk-dummy"
    st.warning("OpenAI API key not found. Using dummy key")

# Ensure necessary variables are in session state for use across pages
if "ELEVENLABS_API_KEY" not in st.session_state:
    st.session_state["ELEVENLABS_API_KEY"] = ELEVENLABS_API_KEY
if "OPENAI_API" not in st.session_state:
    st.session_state["OPENAI_API"] = OPENAI_API

# Initialize session state
if "models" not in st.session_state:
    st.session_state["models"] = fetch_models(ELEVENLABS_API_KEY)
if "voices" not in st.session_state:
    st.session_state["voices"] = fetch_voices(ELEVENLABS_API_KEY)
if "seed" not in st.session_state:
    st.session_state["seed"] = "None"
if "generated_audio" not in st.session_state:
    st.session_state["generated_audio"] = []
if "original_script" not in st.session_state:
    st.session_state["original_script"] = ""
if "enhanced_script" not in st.session_state:
    st.session_state["enhanced_script"] = ""

# Sidebar
sidebar = st.sidebar
with sidebar:
    st.title("Seed Settings")
    seed_type = st.radio("Seed Type", ["Random", "Fixed"])

    if seed_type == "Fixed":
        fixed_seed = sidebar.text_input(
            "Fixed Seed", help="Set a fixed seed to improve reproducibility."
        )
        st.caption(
            """Setting a fixed seed will ensure that the audio generated is consistent across runs.
            For example when using variables in the script."""
        )
    else:
        st.caption("A random seed will be generated for the audio file.")

# Main content
st.title("ElevenTools")

# Create selectboxes for model and voice selection
selected_model_name = st.selectbox(
    "Select model",
    options=[model[1] for model in st.session_state["models"]],
    format_func=lambda x: x,
)
selected_model_id = next(
    model[0] for model in st.session_state["models"] if model[1] == selected_model_name
)

selected_voice_name = st.selectbox(
    "Select voice",
    options=[voice[1] for voice in st.session_state["voices"]],
    format_func=lambda x: x,
)
selected_voice_id = get_voice_id(st.session_state["voices"], selected_voice_name)

# Store selected model and voice IDs in session state
st.session_state["selected_model_id"] = selected_model_id
st.session_state["selected_voice_id"] = selected_voice_id

# Text input
script = st.text_area(
    "Text to speech",
    height=100,
    help="""Use curly braces to add variables.
    `Example: {name} is a {job_title}.`
    Use double square brackets to add phonetic conversion.
    `Example: [[language:word]]`
    """,
)

# Store the original script
if script != st.session_state["original_script"]:
    st.session_state["original_script"] = script
    st.session_state["enhanced_script"] = (
        ""  # Clear enhanced script when original changes
    )

# New prompt input for script enhancement
enhancement_prompt = st.text_input(
    "Enhancement prompt (optional)",
    "",
    help="Provide a prompt to guide the script enhancement process.",
)

# New "Enhance script" button
if st.button("Enhance script"):
    if script:
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(progress):
            progress_bar.progress(progress)
            status_text.text(f"Enhancing script... {progress:.0%}")

        success, result = enhance_script_with_ollama(
            script, enhancement_prompt, update_progress
        )

        progress_bar.empty()
        status_text.empty()

        if success:
            st.session_state["enhanced_script"] = result
            st.success("Script enhanced successfully!")
            st.text_area(
                "Enhanced script", value=st.session_state["enhanced_script"], height=150
            )
        else:
            st.error("Error enhancing script")
            st.error(result)
    else:
        st.warning("Please enter some text to enhance.")

# New "Remove enhancement" button
if st.button("Remove enhancement"):
    if st.session_state["enhanced_script"]:
        st.session_state["enhanced_script"] = ""
        st.success("Enhancement removed. Original script restored.")
    else:
        st.info("No enhancement to remove.")

# Use enhanced script if available, otherwise use original script
script_to_use = (
    st.session_state["enhanced_script"]
    if st.session_state["enhanced_script"]
    else script
)

if script_to_use:
    detected_variables = detect_string_variables(script_to_use)
    detect_phonetic = detect_phonetic_conversion(script_to_use)

    if detected_variables and len(detected_variables) > 0:
        st.info("Detected variables")
        variables_exp = st.expander("Text variables", expanded=True)
        with variables_exp:
            for variable in detected_variables:
                value = st.text_input(f"Edit: {variable}", key=variable)
                if value:
                    script_to_use = script_to_use.replace(f"{{{variable}}}", value)
            st.toast("Updated script", icon="🔄")
            updated_script = st.markdown(f"#### Updated script:\n{script_to_use}")

    if detect_phonetic and len(detect_phonetic) > 0:
        st.info("Detected phonetic conversion")
        phonetic_exp = st.expander("Phonetic conversion", expanded=True)
        with phonetic_exp:
            for phonetic in detect_phonetic:
                language = phonetic[0]
                word = phonetic[1]
                script_to_use = script_to_use.replace(
                    f"[[{language}:{word}]]",
                    convert_word_to_phonetic(
                        word=word, language=language, model=selected_model_id
                    ),
                )
            st.toast("Updated script", icon="🔄")
            st.subheader("Updated script")
            updated_script = st.markdown(script_to_use)

# Voice settings
voice_settings = st.expander("Advanced voice settings", expanded=True)
with voice_settings:
    voice_stability = st.slider("Voice stability", 0.0, 1.0, 0.5)
    voice_similarity = st.slider("Voice similarity", 0.0, 1.0, 0.5)
    voice_style = st.slider("Voice style", 0.0, 1.0, 0.0)
    use_speaker_boost = st.checkbox("Use speaker boost")

# Store voice settings in session state for use in bulk generation page
st.session_state["voice_settings"] = {
    "stability": voice_stability,
    "similarity_boost": voice_similarity,
    "style": voice_style,
    "use_speaker_boost": use_speaker_boost,
}

# Generate audio button
if st.button("Generate Audio"):
    if script_to_use:
        # Determine seed for this generation
        if seed_type == "Fixed":
            if fixed_seed and fixed_seed.isdigit():
                seed = int(fixed_seed)
            else:
                st.error("Fixed seed must be a valid integer.")
                st.stop()
        else:
            seed = random.randint(0, 9999999999)

        temp_filename = f"VID_{selected_voice_name}_SEED_{seed}_UID_{uuid.uuid1()}.mp3"

        try:
            success, response_seed = generate_audio(
                st.session_state["ELEVENLABS_API_KEY"],
                voice_stability,
                selected_model_id,
                voice_similarity,
                voice_style,
                use_speaker_boost,
                selected_voice_id,
                script_to_use,  # Use the enhanced script if available
                temp_filename,
                seed=seed,
            )

            if success:
                st.success(
                    f"Audio generated successfully with seed {response_seed if response_seed else seed}"
                )
                st.session_state["generated_audio"].append(
                    {
                        "filename": temp_filename,
                        "seed": response_seed if response_seed else seed,
                        "voice": selected_voice_name,
                        "model": selected_model_name,
                        "voice_similarity": voice_similarity,
                        "voice_stability": voice_stability,
                        "voice_style": voice_style,
                        "use_speaker_boost": use_speaker_boost,
                        "script": script_to_use,
                    }
                )
                st.audio(temp_filename, format="audio/mp3")
            else:
                st.error("Failed to generate audio. Please see details below.")
                st.error(
                    response_seed
                )  # In this case, response_seed contains the error message
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            logging.error(
                f"Unexpected error in audio generation: {str(e)}", exc_info=True
            )
    else:
        st.warning("Please enter some text to generate audio.")

# Display generated audio history
Generated_audio = st.expander("Generated audio history", expanded=True)
with Generated_audio:
    for audio in st.session_state["generated_audio"]:
        st.write(audio)
        st.audio(audio["filename"], format="audio/mp3")
