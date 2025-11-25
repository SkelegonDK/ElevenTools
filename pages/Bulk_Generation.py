"""Bulk audio generation page for ElevenTools.

This module provides the Streamlit page interface for bulk audio generation,
allowing users to process CSV files with multiple text entries and generate
audio files in batch with variable replacement support.
"""

import os

import pandas as pd
import streamlit as st

from scripts.Elevenlabs_functions import (
    bulk_generate_audio,
    fetch_models,
    fetch_voices,
    get_voice_id,
)
from utils.api_keys import get_elevenlabs_api_key
from utils.error_handling import (
    ConfigurationError,
    handle_error,
    validate_api_key,
)
from utils.model_capabilities import supports_speed
from utils.security import (
    MAX_CSV_SIZE,
    MAX_DF_ROWS,
    sanitize_path_component,
    validate_column_name,
    validate_csv_file_size,
    validate_dataframe_rows,
    validate_path_within_base,
)
from utils.session_manager import cleanup_old_sessions, get_session_bulk_dir


def main() -> None:
    """Main entry point for the Bulk Generation page.

    This function renders the bulk audio generation interface, allowing users to:
    - Upload CSV files with text and optional filename columns
    - Configure voice settings and model selection
    - Generate multiple audio files in batch with variable replacement
    - Monitor generation progress and handle errors

    The function handles API key validation, CSV file processing, variable detection,
    and bulk audio generation using the ElevenLabs API.

    Returns:
        None
    """
    st.set_page_config(page_title="Bulk Generation", page_icon="📚", layout="centered")

    st.title("ElevenTools")
    st.subheader("Bulk Audio Generation")

    # Cleanup old sessions on page load
    cleanup_old_sessions()

    with open("custom_style.css", encoding="utf-8") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

    # Initialize API key
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
        st.info(
            "💡 **Tip**: API keys entered via the Settings page are stored only in your browser session and are never saved to disk or shared between users."
        )
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

    # Sidebar - seed settings removed

    # Fetch models and voices
    if "models" not in st.session_state:
        st.session_state["models"] = fetch_models(ELEVENLABS_API_KEY)
    if "voices" not in st.session_state:
        st.session_state["voices"] = fetch_voices(ELEVENLABS_API_KEY)

    # Model selection
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

    # Voice selection
    selected_voice_name = st.selectbox(
        "Select voice",
        options=[voice[1] for voice in st.session_state["voices"]],
        format_func=lambda x: x,
    )
    selected_voice_id = get_voice_id(st.session_state["voices"], selected_voice_name)

    # Clear speed setting if model changed and new model doesn't support speed
    previous_model_id = st.session_state.get("selected_model_id")
    st.session_state["selected_model_id"] = selected_model_id

    if previous_model_id != selected_model_id:
        if not supports_speed(selected_model_id):
            # Clear any speed-related session state
            if "voice_speed" in st.session_state:
                del st.session_state["voice_speed"]

    # Voice settings
    voice_settings = st.expander("Voice settings", expanded=True)
    with voice_settings:
        # Add speed slider dynamically based on model capabilities
        # Use model_id in key to ensure widget resets when model changes
        voice_speed = None
        if supports_speed(selected_model_id):
            voice_speed = st.slider(
                "Voice speed",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1,
                key=f"bulk_voice_speed_{selected_model_id}",  # Key includes model_id to reset on model change
                help="Adjust the speaking speed (available for multilingual and turbo/flash v2+ models)",
            )
        voice_stability = st.slider("Voice stability", 0.0, 1.0, 0.5)
        voice_similarity = st.slider("Voice similarity", 0.0, 1.0, 0.5)
        voice_style = st.slider("Voice style", 0.0, 1.0, 0.0)
        speaker_boost = st.checkbox("Use speaker boost")

    voice_settings_dict = {
        "stability": voice_stability,
        "similarity_boost": voice_similarity,
        "style": voice_style,
        "use_speaker_boost": speaker_boost,
    }

    if supports_speed(selected_model_id) and voice_speed is not None:
        voice_settings_dict["speed"] = voice_speed

    st.write(
        """
#### Upload a CSV file with the following columns:
- **text:** The text to be converted to speech. Use {variable_name} for variables.
- **filename** (optional): Custom filename for the generated audio.
- Any additional columns will be treated as variables to replace in the text.

**Example CSV content:**
| text | filename | name | job |
| --- | --- | --- | --- |
| Hello {name}! | greeting_{name} | Alice | developer |
| {name} is a {job}. | job_intro_{name} | Bob | designer |
"""
    )

    # Template download button
    template_path = "bulk_template.csv"
    if os.path.exists(template_path):
        try:
            with open(template_path, "rb") as f:
                st.download_button(
                    label="📥 Download CSV Template",
                    data=f.read(),
                    file_name="bulk_template.csv",
                    mime="text/csv",
                    key="download_template",
                    help="Download a template CSV file with example data to get started",
                )
        except Exception as e:
            st.caption(f"Template download unavailable: {str(e)}")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Validate file size
            if not validate_csv_file_size(uploaded_file.size):
                st.error(
                    f"⚠️ File size ({uploaded_file.size / (1024*1024):.2f} MB) exceeds maximum allowed size "
                    f"({MAX_CSV_SIZE / (1024*1024):.2f} MB). Please use a smaller file."
                )
                st.stop()

            df = pd.read_csv(uploaded_file)

            # Validate DataFrame row count
            if not validate_dataframe_rows(len(df)):
                st.error(
                    f"⚠️ CSV file contains {len(df)} rows, which exceeds the maximum allowed ({MAX_DF_ROWS} rows). "
                    f"Please split your file into smaller batches."
                )
                st.stop()

            # Validate column names
            invalid_columns = [
                col for col in df.columns if not validate_column_name(str(col))
            ]
            if invalid_columns:
                st.error(
                    f"⚠️ Invalid column names detected: {', '.join(invalid_columns)}. "
                    "Column names must contain only alphanumeric characters and underscores."
                )
                st.stop()

            # Validate required 'text' column exists
            if "text" not in df.columns:
                st.error("⚠️ CSV file must contain a 'text' column.")
                st.stop()

            st.write("CSV file uploaded successfully. Preview:")
            st.write(df.head())

            if st.button("Generate Bulk Audio"):
                # Sanitize CSV filename to prevent path traversal
                raw_filename = uploaded_file.name.split(".")[0]
                sanitized_filename = sanitize_path_component(raw_filename)

                # Use session-based bulk directory
                output_dir = get_session_bulk_dir(sanitized_filename)

                # Validate that output directory is within session outputs
                outputs_base = os.path.join(os.getcwd(), "outputs")
                if not validate_path_within_base(output_dir, outputs_base):
                    st.error(
                        "⚠️ Invalid output directory path. Path traversal detected."
                    )
                    st.stop()

                success, message = bulk_generate_audio(
                    ELEVENLABS_API_KEY,
                    selected_model_id,
                    selected_voice_id,
                    uploaded_file,
                    output_dir,
                    voice_settings_dict,
                )

                if success:
                    st.success("Bulk generation completed!")
                    st.write(message)
                else:
                    st.error(
                        "Bulk generation failed or produced no results. Please check the logs for more information."
                    )
        except Exception as e:
            st.error(f"An error occurred while processing the CSV file: {str(e)}")
            st.write("Error details:", str(e))
    else:
        st.info("Please upload a CSV file to begin bulk generation.")


if __name__ == "__main__":
    main()
