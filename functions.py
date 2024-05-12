import streamlit as st
import re


@st.experimental_fragment()
def detect_string_variables(text: str):
    """
    Detects string variables in a given text
    """

    return re.findall(r"\{([^}]+)\}", text)
