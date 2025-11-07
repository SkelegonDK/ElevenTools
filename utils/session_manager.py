"""Session management utilities for ElevenTools.

This module provides session-based file organization to ensure privacy
and isolation between users in multi-user cloud deployments.
"""

import os
import uuid
import time
import shutil
import streamlit as st
from typing import Optional


def get_session_id() -> str:
    """Get or create session ID for current user.
    
    Returns:
        Unique session ID string
    """
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]


def get_session_output_dir() -> str:
    """Get output directory for current session.
    
    Returns:
        Path to session-specific output directory
    """
    session_id = get_session_id()
    session_dir = os.path.join(os.getcwd(), "outputs", session_id)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def get_session_single_dir() -> str:
    """Get single output directory for current session.
    
    Returns:
        Path to session-specific single output directory
    """
    session_dir = get_session_output_dir()
    single_dir = os.path.join(session_dir, "single")
    os.makedirs(single_dir, exist_ok=True)
    return single_dir


def get_session_bulk_dir(csv_filename: str) -> str:
    """Get bulk output directory for current session.
    
    Args:
        csv_filename: Sanitized CSV filename
        
    Returns:
        Path to session-specific bulk output directory
    """
    session_dir = get_session_output_dir()
    bulk_base = os.path.join(session_dir, "bulk")
    os.makedirs(bulk_base, exist_ok=True)
    bulk_dir = os.path.join(bulk_base, csv_filename)
    os.makedirs(bulk_dir, exist_ok=True)
    return bulk_dir


def cleanup_old_sessions(max_age_hours: int = 24) -> int:
    """Remove session directories older than max_age_hours.
    
    Args:
        max_age_hours: Maximum age in hours before cleanup (default: 24)
        
    Returns:
        Number of directories removed
    """
    outputs_dir = os.path.join(os.getcwd(), "outputs")
    if not os.path.exists(outputs_dir):
        return 0
    
    removed_count = 0
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for entry in os.listdir(outputs_dir):
            # Skip non-session directories (like old "single" directory)
            if entry == "single" or entry == "bulk":
                continue
            
            session_dir = os.path.join(outputs_dir, entry)
            if os.path.isdir(session_dir):
                # Check directory modification time (most recent file operation)
                try:
                    dir_mtime = os.path.getmtime(session_dir)
                    dir_age = current_time - dir_mtime
                    
                    if dir_age > max_age_seconds:
                        shutil.rmtree(session_dir)
                        removed_count += 1
                except (OSError, PermissionError):
                    # Skip directories we can't access
                    continue
    except (OSError, PermissionError):
        pass
    
    return removed_count

