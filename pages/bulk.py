import streamlit as st
import pandas as pd
import os
from Elevenlabs_functions import (
    bulk_generate_audio,
    fetch_models,
    fetch_voices,
    get_voice_id,
)
import random

st.set_page_config(page_title="Bulk Generation", page_icon="📚", layout="centered")

st.title("Bulk Generation")

# Sidebar for seed input
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
        st.caption("Random seeds will be generated for each audio file.")

# Fetch models and voices
if "models" not in st.session_state:
    st.session_state["models"] = fetch_models(st.session_state["ELEVENLABS_API_KEY"])
if "voices" not in st.session_state:
    st.session_state["voices"] = fetch_voices(st.session_state["ELEVENLABS_API_KEY"])

# Model selection
selected_model_name = st.selectbox(
    "Select model",
    options=[model[1] for model in st.session_state["models"]],
    format_func=lambda x: x,
)
selected_model_id = next(
    model[0] for model in st.session_state["models"] if model[1] == selected_model_name
)

# Voice selection
selected_voice_name = st.selectbox(
    "Select voice",
    options=[voice[1] for voice in st.session_state["voices"]],
    format_func=lambda x: x,
)
selected_voice_id = get_voice_id(st.session_state["voices"], selected_voice_name)

# Voice settings
voice_settings = st.expander("Voice settings", expanded=True)
with voice_settings:
    voice_stability = st.slider("Voice stability", 0.0, 1.0, 0.5)
    voice_similarity = st.slider("Voice similarity", 0.0, 1.0, 0.5)
    voice_style = st.slider("Voice style", 0.0, 1.0, 0.0)
    speaker_boost = st.checkbox("Use speaker boost")

voice_settings_dict = {
    "stability": voice_stability,
    "similarity_boost": voice_similarity,
    "style": voice_style,
    "speaker_boost": speaker_boost,
}

st.write(
    """
Upload a CSV file with the following columns:
- 'text': The text to be converted to speech. Use {variable_name} for variables.
- 'filename' (optional): Custom filename for the generated audio.
- Any additional columns will be treated as variables to replace in the text.

Example CSV content:
```
text,filename,name,job
Hello {name}!,greeting_{name},Alice,developer
{name} is a {job}.,job_intro_{name},Bob,designer
```
"""
)

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("CSV file uploaded successfully. Preview:")
        st.write(df.head())

        if st.button("Generate Bulk Audio"):
            csv_filename = uploaded_file.name.split(".")[0]
            output_dir = os.path.join("bulk_output", csv_filename)
            os.makedirs(output_dir, exist_ok=True)

            # Prepare seed for bulk generation
            if seed_type == "Fixed":
                seed = int(fixed_seed) if fixed_seed.isdigit() else None
            else:
                seed = None  # Random seeds will be generated in the bulk_generate_audio function

            results_df = bulk_generate_audio(
                st.session_state["ELEVENLABS_API_KEY"],
                selected_model_id,
                selected_voice_id,
                uploaded_file,
                output_dir,
                voice_settings_dict,
                seed_type,
                seed,
            )

            if not results_df.empty:
                st.success("Bulk generation completed!")
                st.write("Generation Results:")
                st.write(results_df)

                for index, row in results_df.iterrows():
                    if row["success"]:
                        st.write(f"Audio for: {row['text']}")
                        st.audio(
                            os.path.join(output_dir, row["filename"]),
                            format="audio/mp3",
                        )
            else:
                st.error(
                    "Bulk generation failed or produced no results. Please check the logs for more information."
                )
    except Exception as e:
        st.error(f"An error occurred while processing the CSV file: {str(e)}")
        st.write("Error details:", str(e))
else:
    st.info("Please upload a CSV file to begin bulk generation.")
