import streamlit as st
import os
import re
from datetime import datetime

# Path to the outputs directory
OUTPUTS_DIR = os.path.join(os.getcwd(), "outputs")
SINGLE_DIR = os.path.join(OUTPUTS_DIR, "single")

st.title("File Explorer: Generated Audio")

if not os.path.exists(OUTPUTS_DIR):
    st.info("No generated audio found. The 'outputs' directory does not exist yet.")
    st.stop()
else:
    # --- Helper functions ---
    def parse_single_filename(filename):
        # Expected format: LANGUAGE_VOICE_NAME_DATE_ID.mp3
        pattern = r"^(?P<lang>[^_]+)_(?P<voice>[^_]+)_(?P<date>[^_]+)_(?P<id>[^_]+)\.mp3$"
        match = re.match(pattern, filename)
        if match:
            return match.groupdict()
        return None

    def parse_bulk_filename(filename):
        # Example: praise_{name}.mp3 or similar
        return {"filename": filename}

    # --- Bulk Outputs ---
    st.header("Bulk Outputs")
    bulk_groups = []
    for entry in os.listdir(OUTPUTS_DIR):
        group_path = os.path.join(OUTPUTS_DIR, entry)
        if os.path.isdir(group_path) and entry != "single":
            # Each subfolder is a bulk group named after the CSV file
            group_files = [f for f in os.listdir(group_path) if f.endswith(".mp3")]
            if group_files:
                bulk_groups.append((entry, group_path, group_files))

    if not bulk_groups:
        st.write("No bulk outputs found.")
    else:
        for group_name, group_path, group_files in bulk_groups:
            with st.expander(f"Bulk: {group_name}"):
                for audio_file in group_files:
                    file_path = os.path.join(group_path, audio_file)
                    meta = parse_bulk_filename(audio_file)
                    col1, col2 = st.columns([2, 5])
                    with col1:
                        st.audio(file_path)
                    with col2:
                        st.write(f"**Filename:** {audio_file}")
                        st.write(f"**Source CSV:** {group_name}")
                        # Add more metadata extraction if available (e.g., from a manifest file)

    # --- Single Outputs ---
    st.header("Single Outputs")
    if not os.path.exists(SINGLE_DIR):
        st.write("No single outputs found.")
    else:
        single_files = [f for f in os.listdir(SINGLE_DIR) if f.endswith(".mp3")]
        if not single_files:
            st.write("No single outputs found.")
        else:
            for audio_file in single_files:
                file_path = os.path.join(SINGLE_DIR, audio_file)
                meta = parse_single_filename(audio_file)
                col1, col2 = st.columns([2, 5])
                with col1:
                    st.audio(file_path)
                with col2:
                    st.write(f"**Filename:** {audio_file}")
                    if meta:
                        st.write(f"**Language:** {meta['lang']}")
                        st.write(f"**Voice:** {meta['voice']}")
                        st.write(f"**Date:** {meta['date']}")
                        st.write(f"**ID:** {meta['id']}")
                    else:
                        st.write("_Could not parse metadata from filename._")

    # --- End of File Explorer ---
