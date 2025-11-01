import streamlit as st
from scripts.openrouter_functions import translate_script_with_openrouter
from typing import Optional


def translate_script(text: str, language: str, model: Optional[str] = None) -> str:
    """
    Translate the text to the given language using OpenRouter.
    
    Args:
        text: Text to translate.
        language: Target language.
        model: Optional model to use. If None, uses default model.
        
    Returns:
        Translated text.
    """
    return translate_script_with_openrouter(text, language, model=model)
