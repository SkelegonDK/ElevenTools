"""OpenRouter API integration functions.

This module provides functions for interacting with the OpenRouter API, including
script enhancement, translation, phonetic conversion, and model management.
"""

import html
from difflib import SequenceMatcher
from typing import Any

import requests
import streamlit as st

from utils.api_keys import get_openrouter_api_key
from utils.error_handling import APIError
from utils.model_capabilities import supports_audio_tags

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
DEFAULT_MODEL = "openrouter/auto"  # Use a free model or specify as needed
DEFAULT_TRANSLATION_MODEL = "minimax/minimax-m2:free"
DEFAULT_ENHANCEMENT_MODEL = "minimax/minimax-m2:free"


def enhance_script_for_v3(
    script: str, enhancement_prompt: str = "", progress_callback=None
) -> tuple[bool, str]:
    """Enhance the given script specifically for ElevenLabs v3 models using Audio Tags.

    Audio Tags are square-bracketed tags that provide expressive control:
    - Emotions: [excited], [sad], [angry], [happily], [sorrowful]
    - Delivery: [whispers], [shouts], [x accent]
    - Human reactions: [laughs], [clears throat], [sighs]
    - Sound effects: [gunshot], [clapping], [explosion] (when contextually appropriate)

    Args:
        script (str): The script to enhance.
        enhancement_prompt (str, optional): Optional prompt for enhancement guidance. Defaults to "".
        progress_callback (Callable, optional): Optional callback function to update progress. Defaults to None.

    Returns:
        Tuple[bool, str]: Tuple containing (success, result) where success indicates if enhancement succeeded
            and result contains the enhanced script or error message.
    """
    api_key = get_openrouter_api_key()
    if not api_key:
        return False, "OpenRouter API key not found. Please set it in Settings."

    prompt = f"""
# Enhance the following script for ElevenLabs v3 Text-to-Speech using Audio Tags.

ElevenLabs v3 models support Audio Tags - square-bracketed tags that control emotion, delivery, and natural speech patterns. Use Audio Tags instead of traditional XML tags.

## Apply the following Audio Tags techniques:

### 1. **Emotions** - Set emotional tone:
   - [excited], [sad], [angry], [happily], [sorrowful], [fearful], [confident]
   - Use combinations when appropriate: [excited] then [whispers] for dramatic effect

### 2. **Delivery Direction** - Control tone and performance:
   - [whispers] - For quiet, intimate moments
   - [shouts] - For emphasis or urgency
   - [x accent] - For character voices (e.g., [French accent], [British accent], [American accent])
   - [monotone] - For flat delivery when needed

### 3. **Human Reactions** - Add natural speech patterns:
   - [laughs], [chuckles], [giggles]
   - [clears throat] - For natural pauses or transitions
   - [sighs] - For exhaustion, relief, or contemplation
   - [gasps] - For surprise or shock

### 4. **Sound Effects** - Add contextual audio (use sparingly and only when appropriate):
   - [gunshot], [clapping], [explosion] - Only if the script context requires it
   - These should enhance the narrative, not distract

## Guidelines:
- Place Audio Tags immediately before the text they modify
- Use tags naturally - don't overuse them
- Combine tags when appropriate for nuanced delivery
- Maintain the original meaning and flow of the script
- Audio Tags use square brackets: [tag] not <tag>
- Focus on natural, expressive speech that matches the script's intent

{html.unescape(enhancement_prompt) if enhancement_prompt else 'Use the existing context to improve the script, keeping in mind the Audio Tags techniques and examples provided above.'}

Script to enhance:
{html.unescape(script)}

IMPORTANT: Provide ONLY the enhanced script as your response. Do not include any explanations, notes, or additional text. The enhanced script should use Audio Tags in square brackets [like this] and be ready for ElevenLabs v3 text-to-speech synthesis. Maintain the overall flow and coherence of the original text.
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
                "content": "You are a helpful assistant specializing in ElevenLabs v3 Audio Tags script enhancement. You understand how to use Audio Tags to create expressive, natural-sounding speech.",
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


def enhance_script_with_openrouter(
    script: str,
    enhancement_prompt: str = "",
    progress_callback=None,
    model_id: str | None = None,
) -> tuple[bool, str]:
    """Enhance the given script using OpenRouter's LLM.

    Routes to v3-specific enhancement (Audio Tags) when a v3 model is detected,
    otherwise uses traditional enhancement techniques.

    Args:
        script (str): The script to enhance.
        enhancement_prompt (str, optional): Optional prompt for enhancement guidance. Defaults to "".
        progress_callback (Callable, optional): Optional callback function to update progress. Defaults to None.
        model_id (str, optional): Optional model ID to determine enhancement strategy. Defaults to None.

    Returns:
        Tuple[bool, str]: Tuple containing (success, result) where success indicates if enhancement succeeded
            and result contains the enhanced script or error message.
    """
    # Route to v3-specific enhancement if model supports Audio Tags
    if model_id and supports_audio_tags(model_id):
        return enhance_script_for_v3(script, enhancement_prompt, progress_callback)

    # Use traditional enhancement for non-v3 models
    api_key = get_openrouter_api_key()
    if not api_key:
        return False, "OpenRouter API key not found. Please set it in Settings."

    # Always use default enhancement model for OpenRouter API call
    # (model_id parameter is only for ElevenLabs v3 routing logic)
    openrouter_model_id = get_default_enhancement_model()

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
        "model": openrouter_model_id,
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


def get_openrouter_response(prompt: str, model: str | None = None) -> str:
    """Get a response from OpenRouter using the specified model or default.

    Args:
        prompt (str): The prompt to send to OpenRouter.
        model (str, optional): Model ID to use. If None, uses default model. Defaults to None.

    Returns:
        str: The response text from OpenRouter, or an error message if the request fails.
    """
    api_key = get_openrouter_api_key()
    if not api_key:
        return "OpenRouter API key not found. Please set it in Settings."
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model or DEFAULT_MODEL,
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


def translate_script_with_openrouter(
    text: str, language: str, model: str | None = None
) -> str:
    """
    Translate the text to the given language using OpenRouter.

    Args:
        text: Text to translate.
        language: Target language.
        model: Optional model to use. If None, uses default model from settings.

    Returns:
        Translated text.
    """
    # Use default translation model if no model provided
    if model is None:
        model = get_default_translation_model()

    prompt = f"Translate the following text to {language}:\n\n{text}"
    return get_openrouter_response(prompt, model=model)


def convert_word_to_phonetic_openrouter(
    word: str, language: str, model: str
) -> str | None:
    """Convert a word to its phonetic spelling in a given language using OpenRouter.

    Args:
        word (str): The word to convert to phonetic spelling.
        language (str): The target language for phonetic conversion.
        model (str): The model ID to use for conversion.

    Returns:
        Optional[str]: The phonetic spelling of the word, or None if conversion fails.
    """
    if model == "eleven_monolingual_v1":
        prompt = f"You speak perfect {language}. Convert the word {word} into the phonetic spelling appropriate for the {language} language. Only respond with the phonetic spelling of the word, nothing else."
    else:
        prompt = f"You speak perfect {language}. Your goal is to pronounce this word correctly and help me not sound like a tourist. When I type something in English, you will translate and also give me the phonetic pronunciation. Only respond with the phonetic pronunciation of the word, nothing else."
    result = get_openrouter_response(prompt, model=model)
    return result.strip() if result else None


@st.cache_data(ttl=3600)
def fetch_openrouter_models() -> list[dict[str, Any]]:
    """
    Fetch available models from OpenRouter API.

    Returns:
        List of model dictionaries containing model information.

    Raises:
        APIError: If the API request fails or returns an error response.
    """
    api_key = get_openrouter_api_key()
    if not api_key:
        raise APIError("OpenRouter API key not found. Please set it in Settings.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(OPENROUTER_MODELS_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        raise APIError(f"Failed to fetch models from OpenRouter: {str(e)}")


def identify_free_models(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Identify free models from a list of models.

    A model is considered free if:
    1. Model ID ends with ":free" (e.g., "minimax/minimax-m2:free"), OR
    2. Both pricing.prompt and pricing.completion are 0

    Args:
        models: List of model dictionaries from OpenRouter API.

    Returns:
        List of free model dictionaries.
    """
    free_models = []
    for model in models:
        model_id = model.get("id", "")

        # Check if model ID ends with ":free" (most reliable indicator)
        if model_id.endswith(":free"):
            free_models.append(model)
            continue

        # Fallback: Check pricing (some free models may not have :free suffix)
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", None)
        completion_price = pricing.get("completion", None)

        # Check if both prices are 0 (free)
        if prompt_price == 0 and completion_price == 0:
            free_models.append(model)

    return free_models


def filter_free_models(
    models: list[dict[str, Any]], show_free_only: bool
) -> list[dict[str, Any]]:
    """
    Filter models to show only free models if requested.

    Args:
        models: List of model dictionaries.
        show_free_only: If True, return only free models. If False, return all models.

    Returns:
        Filtered list of model dictionaries.
    """
    if not show_free_only:
        return models
    return identify_free_models(models)


def _fuzzy_match_score(query: str, text: str) -> float:
    """
    Calculate fuzzy match score between query and text.

    Uses SequenceMatcher for similarity scoring (0.0 to 1.0).
    Also checks if query is a substring for partial matches.

    Args:
        query: Search query string.
        text: Text to match against.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    query_lower = query.lower()
    text_lower = text.lower()

    # Exact match gets highest score
    if query_lower == text_lower:
        return 1.0

    # Substring match gets high score
    if query_lower in text_lower:
        return 0.9

    # Calculate similarity using SequenceMatcher
    similarity = SequenceMatcher(None, query_lower, text_lower).ratio()
    return similarity


def search_models_fuzzy(
    models: list[dict[str, Any]], query: str, min_score: float = 0.3
) -> list[dict[str, Any]]:
    """
    Search models using fuzzy matching algorithm.

    Args:
        models: List of model dictionaries to search.
        query: Search query string.
        min_score: Minimum similarity score threshold (0.0 to 1.0). Default 0.3.

    Returns:
        List of matching models sorted by relevance (highest score first).
    """
    # Strip whitespace and treat empty/whitespace-only queries as no search
    if not query or not query.strip():
        return models

    # Use stripped query for matching
    query = query.strip()

    # Calculate scores for each model
    scored_models = []
    for model in models:
        model_name = model.get("id", "")
        model_name_display = model.get("name", model_name)

        # Score based on model ID and name
        id_score = _fuzzy_match_score(query, model_name)
        name_score = _fuzzy_match_score(query, model_name_display)

        # Use the higher score
        score = max(id_score, name_score)

        # Only include models with score above threshold
        if score >= min_score:
            scored_models.append((score, model))

    # Sort by score (descending) and return models
    scored_models.sort(key=lambda x: x[0], reverse=True)
    return [model for _, model in scored_models]


def get_default_translation_model() -> str:
    """
    Get the default translation model from session state or fallback to hardcoded default.

    Returns:
        Model ID string for translation.
    """
    return st.session_state.get("default_translation_model", DEFAULT_TRANSLATION_MODEL)


def get_default_enhancement_model() -> str:
    """
    Get the default enhancement model from session state or fallback to hardcoded default.

    Returns:
        Model ID string for script enhancement.
    """
    return st.session_state.get("default_enhancement_model", DEFAULT_ENHANCEMENT_MODEL)
