import streamlit as st
from scripts.openrouter_functions import translate_script_with_openrouter


def translate_script(text, language):
    """
    Translate the text to the given language using OpenRouter.
    """
    return translate_script_with_openrouter(text, language)
