import streamlit as st
from functions import detect_string_variables, detect_phonetic_conversion
from Openai_functions import convert_word_to_phonetic
from Elevenlabs_functions import (
    generate_audio,
    fetch_models,
    fetch_voices,
    get_voice_id,
)
import uuid
import random
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

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

if script:
    detected_variables = detect_string_variables(script)
    detect_phonetic = detect_phonetic_conversion(script)

    if detected_variables and len(detected_variables) > 0:
        st.info("Detected variables")
        variables_exp = st.expander("Text variables", expanded=True)
        with variables_exp:
            for variable in detected_variables:
                value = st.text_input(f"Edit: {variable}", key=variable)
                if value:
                    script = script.replace(f"{{{variable}}}", value)
            st.toast("Updated script", icon="🔄")
            updated_script = st.markdown(f"#### Updated script:\n{script}")

    if detect_phonetic and len(detect_phonetic) > 0:
        st.info("Detected phonetic conversion")
        phonetic_exp = st.expander("Phonetic conversion", expanded=True)
        with phonetic_exp:
            for phonetic in detect_phonetic:
                language = phonetic[0]
                word = phonetic[1]
                script = script.replace(
                    f"[[{language}:{word}]]",
                    convert_word_to_phonetic(
                        word=word, language=language, model=selected_model_id
                    ),
                )
            st.toast("Updated script", icon="🔄")
            st.subheader("Updated script")
            updated_script = st.markdown(script)

# Voice settings
voice_settings = st.expander("Advanced voice settings", expanded=True)
with voice_settings:
    voice_stability = st.slider("Voice stability", 0.0, 1.0, 0.5)
    voice_similarity = st.slider("Voice similarity", 0.0, 1.0, 0.5)
    voice_style = st.slider("Voice style", 0.0, 1.0, 0.0)
    speaker_boost = st.checkbox("Use speaker boost")

# Store voice settings in session state for use in bulk generation page
st.session_state["voice_settings"] = {
    "stability": voice_stability,
    "similarity_boost": voice_similarity,
    "style": voice_style,
    "speaker_boost": speaker_boost,
}

# Generate audio buttons
col1_generate, col2_generate, empty = st.columns(3, gap="small")

with col1_generate:
    generate_random_btn = col1_generate.button(
        "Generate with random seed", key="generate_audio_random"
    )

    if generate_random_btn:
        random_seed = random.randint(0, 9999999999)
        temp_filename = (
            f"VID_{selected_voice_name}_SEED_{random_seed}_UID_{uuid.uuid1()}.mp3"
        )
        success, response_seed = generate_audio(
            ELEVENLABS_API_KEY,
            voice_stability,
            selected_model_id,
            voice_similarity,
            voice_style,
            speaker_boost,
            selected_voice_id,
            script,
            temp_filename,
            seed=random_seed,
        )
        if success:
            st.session_state["generated_audio"].append(
                {
                    "filename": temp_filename,
                    "seed": response_seed if response_seed else random_seed,
                    "voice": selected_voice_name,
                    "model": selected_model_name,
                    "voice_similarity": voice_similarity,
                    "voice_stability": voice_stability,
                    "voice_style": voice_style,
                    "speaker_boost": speaker_boost,
                    "script": script,
                }
            )

with col2_generate:
    generate_seed_btn = col2_generate.button(
        "Generate with fixed seed", key="generate_audio_seed"
    )
    st.caption(st.session_state["seed"])
    if generate_seed_btn:
        try:
            temp_seed = int(st.session_state["seed"])
            if temp_seed <= 0:
                raise ValueError("Seed must be a positive integer")

            temp_filename = (
                f"VID_{selected_voice_name}_SEED_{temp_seed}_UID_{uuid.uuid1()}.mp3"
            )
            success, response_seed = generate_audio(
                ELEVENLABS_API_KEY,
                voice_stability,
                selected_model_id,
                voice_similarity,
                voice_style,
                speaker_boost,
                selected_voice_id,
                script,
                temp_filename,
                seed=temp_seed,
            )
            if success:
                st.success(
                    f"Audio generated successfully with seed {response_seed if response_seed else temp_seed}"
                )
                st.session_state["seed"] = response_seed if response_seed else temp_seed
                st.session_state["generated_audio"].append(
                    {
                        "filename": temp_filename,
                        "seed": response_seed if response_seed else temp_seed,
                        "voice": selected_voice_name,
                        "model": selected_model_name,
                        "voice_similarity": voice_similarity,
                        "voice_stability": voice_stability,
                        "voice_style": voice_style,
                        "speaker_boost": speaker_boost,
                        "script": script,
                    }
                )
        except ValueError as e:
            st.error(f"Invalid seed value: {e}")
        except Exception as e:
            logging.error(f"Error generating audio: {str(e)}")
            st.error(f"An error occurred while generating audio: {str(e)}")

# Display generated audio
Generated_audio = st.expander("Generated audio", expanded=True)
with Generated_audio:
    for audio in st.session_state["generated_audio"]:
        st.write(audio)
        st.audio(audio["filename"], format="audio/mp3")

# Sidebar
sidebar = st.sidebar
with sidebar:
    st.title("Pro Labs")
    st.write("A professional interface for Elevenlabs")

    fixed_seed = sidebar.text_input(
        "Fixed Seed", help="Set a fixed seed to improve reproducibility."
    )
    st.caption(
        """Setting a fixed seed will ensure that the audio generated is consistent across runs.
        For example when using variables in the script."""
    )
    st.session_state["seed"] = fixed_seed

    settings = sidebar.expander("Settings", expanded=True)
