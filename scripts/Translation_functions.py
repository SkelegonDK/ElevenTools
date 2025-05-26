import streamlit as st
from scripts.ollama_functions import get_ollama_response


def translate_script(text, language):
    """
    Translate the text to the given language using Ollama.
    """
    prompt = f"Translate the following text to {language}:\n\n{text}"
    translation = get_ollama_response(prompt)
    return translation
