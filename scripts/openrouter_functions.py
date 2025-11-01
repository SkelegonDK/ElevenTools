import requests
import html
import streamlit as st
from typing import Optional, Tuple, List, Dict, Any
from difflib import SequenceMatcher
from utils.error_handling import APIError

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
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


def get_openrouter_response(prompt: str, model: Optional[str] = None) -> str:
    """Get a response from OpenRouter using the specified model or default."""
    api_key = get_openrouter_api_key()
    if not api_key:
        return "OpenRouter API key not found. Please set it in API Management."
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


def translate_script_with_openrouter(text: str, language: str, model: Optional[str] = None) -> str:
    """
    Translate the text to the given language using OpenRouter.
    
    Args:
        text: Text to translate.
        language: Target language.
        model: Optional model to use. If None, uses default model.
        
    Returns:
        Translated text.
    """
    prompt = f"Translate the following text to {language}:\n\n{text}"
    return get_openrouter_response(prompt, model=model)


def convert_word_to_phonetic_openrouter(
    word: str, language: str, model: str
) -> Optional[str]:
    """Convert a word to its phonetic spelling in a given language using OpenRouter."""
    if model == "eleven_monolingual_v1":
        prompt = f"You speak perfect {language}. Convert the word {word} into the phonetic spelling appropriate for the {language} language. Only respond with the phonetic spelling of the word, nothing else."
    else:
        prompt = f"You speak perfect {language}. Your goal is to pronounce this word correctly and help me not sound like a tourist. When I type something in English, you will translate and also give me the phonetic pronunciation. Only respond with the phonetic pronunciation of the word, nothing else."
    result = get_openrouter_response(prompt, model=model)
    return result.strip() if result else None


@st.cache_data(ttl=3600)
def fetch_openrouter_models() -> List[Dict[str, Any]]:
    """
    Fetch available models from OpenRouter API.
    
    Returns:
        List of model dictionaries containing model information.
        
    Raises:
        APIError: If the API request fails or returns an error response.
    """
    api_key = get_openrouter_api_key()
    if not api_key:
        raise APIError("OpenRouter API key not found. Please set it in API Management.")
    
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


def identify_free_models(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify free models from a list of models.
    
    A model is considered free if both pricing.prompt and pricing.completion are 0.
    
    Args:
        models: List of model dictionaries from OpenRouter API.
        
    Returns:
        List of free model dictionaries.
    """
    free_models = []
    for model in models:
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", None)
        completion_price = pricing.get("completion", None)
        
        # Check if both prices are 0 (free)
        if prompt_price == 0 and completion_price == 0:
            free_models.append(model)
    
    return free_models


def filter_free_models(models: List[Dict[str, Any]], show_free_only: bool) -> List[Dict[str, Any]]:
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


def search_models_fuzzy(models: List[Dict[str, Any]], query: str, min_score: float = 0.3) -> List[Dict[str, Any]]:
    """
    Search models using fuzzy matching algorithm.
    
    Args:
        models: List of model dictionaries to search.
        query: Search query string.
        min_score: Minimum similarity score threshold (0.0 to 1.0). Default 0.3.
        
    Returns:
        List of matching models sorted by relevance (highest score first).
    """
    if not query:
        return models
    
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
