import requests
import html
import streamlit as st
from typing import Optional, Tuple
from utils.error_handling import APIError

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/auto"  # Use a free model or specify as needed


def get_openrouter_api_key() -> Optional[str]:
    """Get the OpenRouter API key from session state or secrets."""
    return st.session_state.get("OPENROUTER_API_KEY") or st.secrets.get(
        "OPENROUTER_API_KEY"
    )


def enhance_script_with_openrouter(
    script: str, enhancement_prompt: str = "", progress_callback=None
) -> Tuple[bool, str]:
    """
    Enhance the given script using OpenRouter's LLM.
    :param script: The script to enhance
    :param enhancement_prompt: Optional prompt for enhancement guidance
    :param progress_callback: Optional callback function to update progress
    :return: Tuple (success, result)
    """
    api_key = get_openrouter_api_key()
    if not api_key:
        return False, "OpenRouter API key not found. Please set it in API Management."

    prompt = f"""
# Enhance the following script for text-to-speech purposes, focusing on creating a natural and expressive output.

## Apply the following techniques:
1. **Pauses:** Use <break> tags to add natural pauses in speech.
2. **Emotional context:** Use <emotional context> tags to convey emotions.
3. **Emphasis:** Apply strategic capitalization for important words or phrases.
4. **Pacing:** Add descriptive language to control speed and rhythm.
5. **Question emphasis:** Use multiple question marks for dramatic effect.
6. **Dynamic speech:** Vary sentence structure and emphasis.
7. **Pronunciation:** Use <phoneme> tags for unusual pronunciations.

{html.unescape(enhancement_prompt) if enhancement_prompt else 'Use the existing context to improve the script, keeping in mind the techniques and examples provided above.'}

Script to enhance:
{html.unescape(script)}

IMPORTANT: Provide ONLY the enhanced script as your response. Do not include any explanations, notes, or additional text. The enhanced script should be ready for text-to-speech synthesis and maintain the overall flow and coherence of the original text.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": DEFAULT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant for text-to-speech script enhancement.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
    }
    try:
        if progress_callback:
            progress_callback(0.0)
        response = requests.post(
            OPENROUTER_API_URL, headers=headers, json=data, timeout=60
        )
        if progress_callback:
            progress_callback(0.99)
        response.raise_for_status()
        result = response.json()
        enhanced_script = result["choices"][0]["message"]["content"].strip()
        return True, enhanced_script
    except Exception as e:
        return False, f"OpenRouter API error: {str(e)}"


def get_openrouter_response(prompt: str) -> str:
    """Get a response from OpenRouter using the default model."""
    api_key = get_openrouter_api_key()
    if not api_key:
        return "OpenRouter API key not found. Please set it in API Management."
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 512,
        "temperature": 0.7,
    }
    try:
        response = requests.post(
            OPENROUTER_API_URL, headers=headers, json=data, timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"OpenRouter API error: {str(e)}"


def translate_script_with_openrouter(text: str, language: str) -> str:
    """Translate the text to the given language using OpenRouter."""
    prompt = f"Translate the following text to {language}:\n\n{text}"
    return get_openrouter_response(prompt)


def convert_word_to_phonetic_openrouter(
    word: str, language: str, model: str
) -> Optional[str]:
    """Convert a word to its phonetic spelling in a given language using OpenRouter."""
    if model == "eleven_monolingual_v1":
        prompt = f"You speak perfect {language}. Convert the word {word} into the phonetic spelling appropriate for the {language} language. Only respond with the phonetic spelling of the word, nothing else."
    else:
        prompt = f"You speak perfect {language}. Your goal is to pronounce this word correctly and help me not sound like a tourist. When I type something in English, you will translate and also give me the phonetic pronunciation. Only respond with the phonetic pronunciation of the word, nothing else."
    result = get_openrouter_response(prompt)
    return result.strip() if result else None
