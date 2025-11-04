import uuid
import random
import logging
import os
from datetime import datetime
import streamlit as st
from scripts.functions import detect_string_variables, detect_phonetic_conversion
from scripts.Elevenlabs_functions import (
    generate_audio,
    fetch_models,
    fetch_voices,
    get_voice_id,
)
from scripts.openrouter_functions import (
    enhance_script_with_openrouter,
    convert_word_to_phonetic_openrouter,
    get_default_enhancement_model,
)

from utils.error_handling import (
    handle_error,
    validate_api_key,
    ProgressManager,
    APIError,
    ValidationError,
    ConfigurationError,
)
from utils.model_capabilities import supports_speed, supports_audio_tags
from utils.api_keys import get_elevenlabs_api_key


# Configure logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="ElevenTools", page_icon="🔊", layout="wide")


try:
    with open("custom_style.css", encoding="utf-8") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    handle_error(e)

# Initialize API keys
ELEVENLABS_API_KEY = get_elevenlabs_api_key()

if not ELEVENLABS_API_KEY:
    st.error("🔑 **ElevenLabs API Key Required**")
    st.markdown(
        """
        No ElevenLabs API key found. Please provide your API key using one of the following methods:
        
        1. **Via Settings Page** (Recommended for cloud deployment):
           - Navigate to the **Settings** page in the sidebar
           - Enter your API key (stored only in your browser session)
        
        2. **Via Streamlit Secrets** (For Streamlit Cloud):
           - Configure secrets in your Streamlit Cloud app settings
           - See [Streamlit Cloud Secrets Documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
        
        3. **Via Local secrets.toml** (For local development):
           - Add your key to `.streamlit/secrets.toml`:
           ```toml
           ELEVENLABS_API_KEY = "your-api-key-here"
           ```
        """
    )
    st.info("💡 **Tip**: API keys entered via the Settings page are stored only in your browser session and are never saved to disk or shared between users.")
    st.stop()

# Validate API key format
try:
    validate_api_key(ELEVENLABS_API_KEY, "ElevenLabs")
except ConfigurationError as e:
    handle_error(e)
    st.markdown(
        "💡 **Need help?** Visit the **Settings** page to update your API key."
    )
    st.stop()

# Initialize session state with progress tracking
progress = ProgressManager(total_steps=4)
try:
    if "models" not in st.session_state:
        progress.update(1, "Fetching available models")
        st.session_state["models"] = fetch_models(ELEVENLABS_API_KEY)

    if "voices" not in st.session_state:
        progress.update(2, "Fetching available voices")
        st.session_state["voices"] = fetch_voices(ELEVENLABS_API_KEY)


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

# Sidebar - seed settings removed

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
    # Clear speed setting if model changed and new model doesn't support speed
    previous_model_id = st.session_state.get("selected_model_id")
    st.session_state["selected_model_id"] = selected_model_id
    st.session_state["selected_voice_id"] = selected_voice_id
    
    # Clear speed from voice_settings if model changed to one that doesn't support speed
    if previous_model_id != selected_model_id:
        if not supports_speed(selected_model_id) and "voice_settings" in st.session_state:
            st.session_state["voice_settings"].pop("speed", None)

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

# Script enhancement section with settings gear icon
st.subheader("Script Enhancement")
col_enhance_title, col_enhance_settings = st.columns([10, 1])
with col_enhance_title:
    st.markdown("Configure script enhancement settings below.")
with col_enhance_settings:
    if st.button("⚙️", help="Open Settings to configure default enhancement model", key="enhancement_settings_btn"):
        st.switch_page("pages/Settings.py")

# New prompt input for script enhancement
# Show v3-specific help text if v3 model is selected
selected_model_id_for_help = st.session_state.get("selected_model_id", "")
is_v3_model = supports_audio_tags(selected_model_id_for_help) if selected_model_id_for_help else False

enhancement_help_text = (
    "Provide a prompt to guide the script enhancement process."
    if not is_v3_model
    else "Provide a prompt to guide the script enhancement process. "
    "Using v3 Audio Tags enhancement: tags like [excited], [whispers], [sighs] will be used."
)

enhancement_prompt = st.text_input(
    "Enhancement prompt (optional)",
    "",
    help=enhancement_help_text,
)

# Script enhancement with progress tracking
if st.button("Enhance script"):
    if not script:
        st.warning("⚠️ Please enter some text to enhance.")
    else:
        progress = ProgressManager()
        try:
            # Get selected ElevenLabs model ID for v3 routing logic
            selected_elevenlabs_model_id = st.session_state.get("selected_model_id")
            
            # Get default enhancement model for OpenRouter API call
            default_enhancement = get_default_enhancement_model()
            if not default_enhancement:
                st.warning(
                    "⚠️ No enhancement model configured. Please configure a default model in Settings (⚙️)."
                )
                st.stop()
            
            st.info(f"ℹ️ Using default enhancement model: **{default_enhancement}** (configure in Settings ⚙️)")
            
            # Check if selected ElevenLabs model supports v3 Audio Tags for routing
            # Pass ElevenLabs model ID for routing logic, but OpenRouter uses default enhancement model
            is_v3 = supports_audio_tags(selected_elevenlabs_model_id) if selected_elevenlabs_model_id else False
            
            # Show indicator if using v3 enhancement
            if is_v3:
                st.info("🎙️ Using v3 Audio Tags enhancement for expressive speech generation")

            def update_progress(prog):
                progress.update(int(prog * 100), "Enhancing script")

            # Pass ElevenLabs model ID for routing (v3 vs traditional), function will use default for OpenRouter API
            success, result = enhance_script_with_openrouter(
                script, enhancement_prompt, update_progress, model_id=selected_elevenlabs_model_id
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
                        phonetic_text = convert_word_to_phonetic_openrouter(
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
    # Add speed slider dynamically based on model capabilities
    # Use model_id in key to ensure widget resets when model changes
    voice_speed = None
    if supports_speed(selected_model_id):
        # Reset to default 1.0 when model changes (key includes model_id, so Streamlit will reset automatically)
        voice_speed = st.slider(
            "Voice speed",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key=f"voice_speed_{selected_model_id}",  # Key includes model_id to reset on model change
            help="Adjust the speaking speed (available for multilingual and turbo/flash v2+ models)",
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

if supports_speed(selected_model_id) and voice_speed is not None:
    st.session_state["voice_settings"]["speed"] = voice_speed

# Generate audio with progress tracking
if st.button("Generate Audio"):
    if not script_to_use:
        st.warning("⚠️ Please enter some text to generate audio.")
    else:
        progress = ProgressManager()
        try:
            # Prepare output directory and filename for single outputs
            single_output_dir = os.path.join(os.getcwd(), "outputs", "single")
            os.makedirs(single_output_dir, exist_ok=True)
            # Use 'unknown' as language for now (extend if language selection is added)
            language = "unknown"
            date_str = datetime.now().strftime("%Y%m%d")
            unique_id = str(uuid.uuid4())[:8]
            temp_filename = (
                f"{language}_{selected_voice_name}_{date_str}_{unique_id}.mp3"
            )
            output_path = os.path.join(single_output_dir, temp_filename)

            progress.update(25, "Initializing audio generation")
            success = generate_audio(
                st.session_state["ELEVENLABS_API_KEY"],
                voice_stability,
                selected_model_id,
                voice_similarity,
                voice_style,
                use_speaker_boost,
                selected_voice_id,
                script_to_use,
                output_path,
                speed=voice_speed if supports_speed(selected_model_id) else None,
            )

            if success:
                progress.complete()
                st.success("✅ Audio generated successfully")
                st.session_state["generated_audio"].append(
                    {
                        "filename": temp_filename,
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
