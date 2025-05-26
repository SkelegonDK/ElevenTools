import streamlit as st
from scripts.functions import detect_string_variables, detect_phonetic_conversion
from scripts.Elevenlabs_functions import (
    generate_audio,
    fetch_models,
    fetch_voices,
    get_voice_id,
)
from scripts.ollama_functions import (
    enhance_script_with_ollama,
    convert_word_to_phonetic,
)
from utils.error_handling import (
    handle_error,
    validate_api_key,
    ProgressManager,
    APIError,
    ValidationError,
    ConfigurationError,
)
import uuid
import random
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="ElevenTools", page_icon="🔊", layout="wide")


try:
    with open("custom_style.css", encoding="utf-8") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    handle_error(e)

# Initialize API keys
try:
    ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
    # Removed OpenAI_API key initialization
    # Validate API key
    validate_api_key(ELEVENLABS_API_KEY, "ElevenLabs")
except Exception as e:
    handle_error(e)
    st.stop()

# Ensure necessary variables are in session state for use across pages
if "ELEVENLABS_API_KEY" not in st.session_state:
    st.session_state["ELEVENLABS_API_KEY"] = ELEVENLABS_API_KEY

# Initialize session state with progress tracking
progress = ProgressManager(total_steps=4)
try:
    if "models" not in st.session_state:
        progress.update(1, "Fetching available models")
        st.session_state["models"] = fetch_models(ELEVENLABS_API_KEY)

    if "voices" not in st.session_state:
        progress.update(2, "Fetching available voices")
        st.session_state["voices"] = fetch_voices(ELEVENLABS_API_KEY)

    if "seed" not in st.session_state:
        progress.update(3, "Initializing session")
        st.session_state["seed"] = "None"

    if "generated_audio" not in st.session_state:
        st.session_state["generated_audio"] = []

    if "original_script" not in st.session_state:
        st.session_state["original_script"] = ""

    if "enhanced_script" not in st.session_state:
        st.session_state["enhanced_script"] = ""

    progress.update(4, "Setup complete")
    progress.complete()
except Exception as e:
    progress.complete(success=False)
    handle_error(e)
    st.stop()

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
st.subheader("Advanced Text-to-Speech")

try:
    # Create selectboxes for model and voice selection
    selected_model_name = st.selectbox(
        "Select model",
        options=[model[1] for model in st.session_state["models"]],
        format_func=lambda x: x,
    )
    selected_model_id = next(
        model[0]
        for model in st.session_state["models"]
        if model[1] == selected_model_name
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

except Exception as e:
    handle_error(e)
    st.stop()

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

# Script enhancement with progress tracking
if st.button("Enhance script"):
    if not script:
        st.warning("⚠️ Please enter some text to enhance.")
    else:
        progress = ProgressManager()
        try:

            def update_progress(prog):
                progress.update(int(prog * 100), "Enhancing script")

            success, result = enhance_script_with_ollama(
                script, enhancement_prompt, update_progress
            )

            if success:
                st.session_state["enhanced_script"] = result
                progress.complete()
                st.text_area(
                    "Enhanced script",
                    value=st.session_state["enhanced_script"],
                    height=150,
                )
            else:
                progress.complete(success=False)
                raise APIError("Failed to enhance script", result)

        except Exception as e:
            progress.complete(success=False)
            handle_error(e)

# Remove enhancement
if st.button("Remove enhancement"):
    if st.session_state["enhanced_script"]:
        st.session_state["enhanced_script"] = ""
        st.success("✅ Enhancement removed. Original script restored.")
    else:
        st.info("ℹ️ No enhancement to remove.")

# Use enhanced script if available, otherwise use original script
script_to_use = (
    st.session_state["enhanced_script"]
    if st.session_state["enhanced_script"]
    else script
)

if script_to_use:
    try:
        detected_variables = detect_string_variables(script_to_use)
        detect_phonetic = detect_phonetic_conversion(script_to_use)

        if detected_variables and len(detected_variables) > 0:
            st.info("🔍 Detected variables")
            variables_exp = st.expander("Text variables", expanded=True)
            with variables_exp:
                for variable in detected_variables:
                    value = st.text_input(f"Edit: {variable}", key=variable)
                    if value:
                        script_to_use = script_to_use.replace(f"{{{variable}}}", value)
                st.toast("Updated script", icon="🔄")
                st.markdown(f"#### Updated script:\n{script_to_use}")

        if detect_phonetic and len(detect_phonetic) > 0:
            st.info("🔍 Detected phonetic conversion")
            phonetic_exp = st.expander("Phonetic conversion", expanded=True)
            with phonetic_exp:
                progress = ProgressManager(len(detect_phonetic))
                for idx, phonetic in enumerate(detect_phonetic):
                    language = phonetic[0]
                    word = phonetic[1]
                    progress.update(idx + 1, f"Converting {word} to phonetic")
                    try:
                        phonetic_text = convert_word_to_phonetic(
                            word=word, language=language, model=selected_model_id
                        )
                        script_to_use = script_to_use.replace(
                            f"[[{language}:{word}]]", phonetic_text
                        )
                    except Exception as e:
                        handle_error(e)
                progress.complete()
                st.toast("Updated script", icon="🔄")
                st.subheader("Updated script")
                st.markdown(script_to_use)
    except Exception as e:
        handle_error(e)

# Voice settings
voice_settings = st.expander("Advanced voice settings", expanded=True)
with voice_settings:
    # Add speed slider for multilingual v2 model
    voice_speed = None
    if selected_model_id == "eleven_multilingual_v2":
        voice_speed = st.slider(
            "Voice speed",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Adjust the speaking speed (only available for multilingual v2 model)",
        )
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

if selected_model_id == "eleven_multilingual_v2":
    st.session_state["voice_settings"]["speed"] = voice_speed

# Generate audio with progress tracking
if st.button("Generate Audio"):
    if not script_to_use:
        st.warning("⚠️ Please enter some text to generate audio.")
    else:
        progress = ProgressManager()
        try:
            # Determine seed for this generation
            if seed_type == "Fixed":
                if not fixed_seed or not fixed_seed.isdigit():
                    raise ValidationError(
                        "Invalid fixed seed", "Fixed seed must be a valid integer."
                    )
                seed = int(fixed_seed)
            else:
                seed = random.randint(0, 9999999999)

            # Prepare output directory and filename for single outputs
            single_output_dir = os.path.join(os.getcwd(), "outputs", "single")
            os.makedirs(single_output_dir, exist_ok=True)
            # Use 'unknown' as language for now (extend if language selection is added)
            language = "unknown"
            date_str = datetime.now().strftime("%Y%m%d")
            unique_id = str(uuid.uuid4())[:8]
            temp_filename = (
                f"{language}_{selected_voice_name}_{date_str}_{unique_id}_{seed}.mp3"
            )
            output_path = os.path.join(single_output_dir, temp_filename)

            progress.update(25, "Initializing audio generation")
            success, response_seed = generate_audio(
                st.session_state["ELEVENLABS_API_KEY"],
                voice_stability,
                selected_model_id,
                voice_similarity,
                voice_style,
                use_speaker_boost,
                selected_voice_id,
                script_to_use,
                output_path,
                seed=seed,
                speed=(
                    voice_speed
                    if selected_model_id == "eleven_multilingual_v2"
                    else None
                ),
            )

            if success:
                progress.complete()
                st.success(
                    f"✅ Audio generated successfully with seed {response_seed if response_seed else seed}"
                )
                st.session_state["generated_audio"].append(
                    {
                        "filename": temp_filename,
                        "seed": response_seed if response_seed else seed,
                        "voice": selected_voice_name,
                        "text": script_to_use,
                        "path": output_path,
                    }
                )
            else:
                progress.complete(success=False)
                raise APIError("Failed to generate audio")

        except Exception as e:
            progress.complete(success=False)
            handle_error(e)

# Display generated audio history
Generated_audio = st.expander("Generated audio history", expanded=True)
with Generated_audio:
    for audio in st.session_state["generated_audio"]:
        st.write(audio)
        st.audio(audio["path"], format="audio/mp3")
