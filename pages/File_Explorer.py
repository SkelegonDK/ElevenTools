import streamlit as st
import os
import re
from datetime import datetime
from utils.security import validate_path_within_base, escape_html_content

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
    abs_outputs_dir = os.path.abspath(OUTPUTS_DIR)
    for entry in os.listdir(OUTPUTS_DIR):
        # Validate entry is safe (not a traversal attempt)
        if entry in ('.', '..') or '/' in entry or '\\' in entry:
            continue
        
        group_path = os.path.join(OUTPUTS_DIR, entry)
        
        # Validate path is within outputs directory
        if not validate_path_within_base(os.path.abspath(group_path), abs_outputs_dir):
            continue
        
        if os.path.isdir(group_path) and entry != "single":
            # Each subfolder is a bulk group named after the CSV file
            try:
                group_files = [f for f in os.listdir(group_path) if f.endswith(".mp3")]
                # Validate each filename
                safe_group_files = []
                for f in group_files:
                    file_path = os.path.join(group_path, f)
                    if validate_path_within_base(os.path.abspath(file_path), os.path.abspath(group_path)):
                        safe_group_files.append(f)
                if safe_group_files:
                    bulk_groups.append((entry, group_path, safe_group_files))
            except (OSError, PermissionError):
                # Skip directories we can't read
                continue

    if not bulk_groups:
        st.write("No bulk outputs found.")
    else:
        for group_name, group_path, group_files in bulk_groups:
            # Escape group name before display
            safe_group_name = escape_html_content(group_name)
            with st.expander(f"Bulk: {safe_group_name}"):
                for audio_file in group_files:
                    file_path = os.path.join(group_path, audio_file)
                    meta = parse_bulk_filename(audio_file)
                    # Escape filename before display
                    safe_filename = escape_html_content(audio_file)
                    col1, col2 = st.columns([2, 5])
                    with col1:
                        st.audio(file_path)
                    with col2:
                        st.write(f"**Filename:** {safe_filename}")
                        st.write(f"**Source CSV:** {safe_group_name}")
                        # Add more metadata extraction if available (e.g., from a manifest file)

    # --- Single Outputs ---
    st.header("Single Outputs")
    if not os.path.exists(SINGLE_DIR):
        st.write("No single outputs found.")
    else:
        abs_single_dir = os.path.abspath(SINGLE_DIR)
        try:
            all_files = os.listdir(SINGLE_DIR)
            single_files = []
            for f in all_files:
                if f.endswith(".mp3"):
                    file_path = os.path.join(SINGLE_DIR, f)
                    # Validate file path is within single directory
                    if validate_path_within_base(os.path.abspath(file_path), abs_single_dir):
                        single_files.append(f)
        except (OSError, PermissionError):
            single_files = []
        
        if not single_files:
            st.write("No single outputs found.")
        else:
            for audio_file in single_files:
                file_path = os.path.join(SINGLE_DIR, audio_file)
                meta = parse_single_filename(audio_file)
                # Escape filename and metadata before display
                safe_filename = escape_html_content(audio_file)
                col1, col2 = st.columns([2, 5])
                with col1:
                    st.audio(file_path)
                with col2:
                    st.write(f"**Filename:** {safe_filename}")
                    if meta:
                        st.write(f"**Language:** {escape_html_content(meta['lang'])}")
                        st.write(f"**Voice:** {escape_html_content(meta['voice'])}")
                        st.write(f"**Date:** {escape_html_content(meta['date'])}")
                        st.write(f"**ID:** {escape_html_content(meta['id'])}")
                    else:
                        st.write("_Could not parse metadata from filename._")

    # --- End of File Explorer ---
