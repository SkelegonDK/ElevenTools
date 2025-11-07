import streamlit as st
import os
import re
import zipfile
import io
from datetime import datetime
from utils.security import validate_path_within_base, escape_html_content
from utils.session_manager import get_session_id, get_session_output_dir, cleanup_old_sessions

# Cleanup old sessions on page load
cleanup_old_sessions()

# Get current session directory
session_id = get_session_id()
session_output_dir = get_session_output_dir()
session_single_dir = os.path.join(session_output_dir, "single")
session_bulk_dir = os.path.join(session_output_dir, "bulk")

st.title("File Explorer: Generated Audio")
st.info(f"📁 **Session ID:** `{session_id[:8]}...` (Your files are private to this session)")

if not os.path.exists(session_output_dir):
    st.info("No generated audio found for this session. Generate some audio to see it here!")
    st.stop()

# Helper functions
def parse_single_filename(filename):
    """Parse single output filename to extract metadata."""
    pattern = r"^(?P<lang>[^_]+)_(?P<voice>[^_]+)_(?P<date>[^_]+)_(?P<id>[^_]+)\.mp3$"
    match = re.match(pattern, filename)
    if match:
        return match.groupdict()
    return None

def parse_bulk_filename(filename):
    """Parse bulk output filename."""
    return {"filename": filename}

def create_zip_archive(file_paths, zip_filename):
    """Create a ZIP archive from file paths.
    
    Args:
        file_paths: List of file paths to include in ZIP
        zip_filename: Name for the ZIP file
        
    Returns:
        BytesIO buffer containing ZIP file data
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            if os.path.exists(file_path):
                arcname = os.path.basename(file_path)
                zip_file.write(file_path, arcname)
    zip_buffer.seek(0)
    return zip_buffer.read()

# --- Bulk Outputs ---
st.header("Bulk Outputs")
bulk_groups = []
if os.path.exists(session_bulk_dir):
    abs_bulk_dir = os.path.abspath(session_bulk_dir)
    for entry in os.listdir(session_bulk_dir):
        # Validate entry is safe (not a traversal attempt)
        if entry in ('.', '..') or '/' in entry or '\\' in entry:
            continue
        
        group_path = os.path.join(session_bulk_dir, entry)
        
        # Validate path is within bulk directory
        if not validate_path_within_base(os.path.abspath(group_path), abs_bulk_dir):
            continue
        
        if os.path.isdir(group_path):
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
    st.write("No bulk outputs found for this session.")
else:
    # Download all bulk files button
    all_bulk_files = []
    for _, group_path, group_files in bulk_groups:
        for f in group_files:
            all_bulk_files.append(os.path.join(group_path, f))
    
    if all_bulk_files:
        try:
            zip_data = create_zip_archive(all_bulk_files, f"bulk_{session_id[:8]}.zip")
            st.download_button(
                label="📦 Download All Bulk Files",
                data=zip_data,
                file_name=f"bulk_{session_id[:8]}.zip",
                mime="application/zip",
                key="download_all_bulk"
            )
        except Exception as e:
            st.warning(f"Could not create bulk download: {str(e)}")
    
    for group_name, group_path, group_files in bulk_groups:
        # Escape group name before display
        safe_group_name = escape_html_content(group_name)
        with st.expander(f"Bulk: {safe_group_name}"):
            # Download button for this group
            group_files_full = [os.path.join(group_path, f) for f in group_files]
            if group_files_full:
                try:
                    group_zip = create_zip_archive(group_files_full, f"{safe_group_name}.zip")
                    st.download_button(
                        label=f"📦 Download {safe_group_name}",
                        data=group_zip,
                        file_name=f"{safe_group_name}.zip",
                        mime="application/zip",
                        key=f"bulk_dl_{group_name}"
                    )
                except Exception as e:
                    st.caption(f"Download unavailable: {str(e)}")
            
            for audio_file in group_files:
                file_path = os.path.join(group_path, audio_file)
                meta = parse_bulk_filename(audio_file)
                # Escape filename before display
                safe_filename = escape_html_content(audio_file)
                col1, col2, col3 = st.columns([2, 4, 1])
                with col1:
                    st.audio(file_path)
                with col2:
                    st.write(f"**Filename:** {safe_filename}")
                    st.write(f"**Source CSV:** {safe_group_name}")
                with col3:
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="⬇️",
                                    data=f.read(),
                                    file_name=audio_file,
                                    mime="audio/mpeg",
                                    key=f"dl_{group_name}_{audio_file}"
                                )
                        except Exception:
                            st.caption("Download unavailable")

# --- Single Outputs ---
st.header("Single Outputs")
single_files = []
if os.path.exists(session_single_dir):
    abs_single_dir = os.path.abspath(session_single_dir)
    try:
        all_files = os.listdir(session_single_dir)
        for f in all_files:
            if f.endswith(".mp3"):
                file_path = os.path.join(session_single_dir, f)
                # Validate file path is within single directory
                if validate_path_within_base(os.path.abspath(file_path), abs_single_dir):
                    single_files.append(f)
    except (OSError, PermissionError):
        pass

if not single_files:
    st.write("No single outputs found for this session.")
else:
    # Download all single files button
    all_single_paths = [os.path.join(session_single_dir, f) for f in single_files]
    if all_single_paths:
        try:
            zip_data = create_zip_archive(all_single_paths, f"single_{session_id[:8]}.zip")
            st.download_button(
                label="📦 Download All Single Files",
                data=zip_data,
                file_name=f"single_{session_id[:8]}.zip",
                mime="application/zip",
                key="download_all_single"
            )
        except Exception as e:
            st.warning(f"Could not create single files download: {str(e)}")
    
    for audio_file in single_files:
        file_path = os.path.join(session_single_dir, audio_file)
        meta = parse_single_filename(audio_file)
        # Escape filename and metadata before display
        safe_filename = escape_html_content(audio_file)
        col1, col2, col3 = st.columns([2, 4, 1])
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
        with col3:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="⬇️",
                            data=f.read(),
                            file_name=audio_file,
                            mime="audio/mpeg",
                            key=f"dl_single_{audio_file}"
                        )
                except Exception:
                    st.caption("Download unavailable")

# --- End of File Explorer ---
