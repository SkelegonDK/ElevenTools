import streamlit as st
import re
import openai


@st.experimental_fragment()
def detect_string_variables(text: str):
    """
    Detects string variables in a given text
    """

    return re.findall(r"\{([^}]+)\}", text)


@st.experimental_fragment()
def detect_phonetic_variables(text: str):
    """
    detect string variables in double square brackets.
    """
    return re.findall(r"\[\[([^]]+)\]\]", text)


# detect phonetic conversion string format is [[language:word]]


def detect_phonetic_conversion(script: str):
    """
    detect phonetic conversion string format is [[language:word]], and returns a lis of dictoinaries with language and word.
    example: [{
        "language": "english",
        "word": "hello"
    }]
    """
    return re.findall(r"\[\[([^:]+):([^]]+)\]\]", script)
