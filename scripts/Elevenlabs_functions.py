"""ElevenLabs API integration functions.

This module provides functions for interacting with the ElevenLabs Text-to-Speech API,
including voice management, audio generation, and voice preview functionality.
"""

import os
import json
import logging
import re
import random
from typing import Tuple, List, Dict, Optional, Any, Union, BinaryIO

try:
    import pandas as pd  # type: ignore
    import requests  # type: ignore
except ImportError:
    pass  # Handle missing dependencies gracefully

import base64
import streamlit as st

from utils.error_handling import APIError, ValidationError, handle_error
from utils.caching import st_cache


@st_cache(ttl_minutes=60)
def fetch_models(api_key: str) -> List[Tuple[str, str]]:
    """Fetch available models from ElevenLabs API.

    Args:
        api_key (str): ElevenLabs API key for authentication.

    Returns:
        List[Tuple[str, str]]: List of tuples containing (model_id, model_name) pairs.

    Raises:
        APIError: If the API request fails or returns an error response.
    """
    url = "https://api.elevenlabs.io/v1/models"
    headers = {"xi-api-key": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        models = response.json()
        return [(model["model_id"], model["name"]) for model in models]
    except requests.exceptions.RequestException as e:
        raise APIError(f"Failed to fetch models", str(e))


@st_cache(ttl_minutes=60)
def fetch_voices(api_key: str) -> List[Tuple[str, str]]:
    """Fetch available voices from ElevenLabs API.

    Args:
        api_key (str): ElevenLabs API key for authentication.

    Returns:
        List[Tuple[str, str]]: List of tuples containing (voice_id, voice_name) pairs.

    Raises:
        APIError: If the API request fails or returns an error response.
    """
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        voices = response.json()["voices"]
        return [(voice["voice_id"], voice["name"]) for voice in voices]
    except requests.exceptions.RequestException as e:
        raise APIError(f"Failed to fetch voices", str(e))


@st_cache(ttl_minutes=60)
def get_voice_id(
    voices: List[Tuple[str, str]], selected_voice_name: str
) -> Optional[str]:
    """Get voice ID for selected voice name.

    Args:
        voices (List[Tuple[str, str]]): List of (voice_id, voice_name) tuples.
        selected_voice_name (str): Name of the selected voice to find ID for.

    Returns:
        Optional[str]: The voice ID if found, None if the voice name doesn't exist.
    """
    for voice_id, name in voices:
        if name == selected_voice_name:
            return voice_id
    return None


def generate_audio(
    xi_api_key: str,
    stability: float,
    model_id: str,
    similarity_boost: float,
    style: float,
    use_speaker_boost: bool,
    voice_id: str,
    text_to_speak: str,
    output_path: str = "output.mp3",
    seed: Optional[int] = None,
    language_code: Optional[str] = None,
    speed: Optional[float] = None,
) -> Tuple[bool, Optional[str]]:
    """Generate audio using ElevenLabs Text-to-Speech API.

    Args:
        xi_api_key (str): ElevenLabs API key for authentication.
        stability (float): Voice stability between 0 and 1.
        model_id (str): ID of the model to use for generation.
        similarity_boost (float): Voice similarity boost between 0 and 1.
        style (float): Voice style between 0 and 1.
        use_speaker_boost (bool): Whether to use speaker boost.
        voice_id (str): ID of the voice to use.
        text_to_speak (str): Text to convert to speech.
        output_path (str, optional): Path to save the audio file. Defaults to "output.mp3".
        seed (Optional[int], optional): Seed for reproducible generation. Defaults to None.
        language_code (Optional[str], optional): Language code for multilingual models. Defaults to None.
        speed (Optional[float], optional): Speed multiplier between 0.5 and 2.0. Only for multilingual v2 model. Defaults to None.

    Returns:
        Tuple[bool, Optional[str]]: Tuple containing (success status, generation seed if successful).

    Raises:
        ValidationError: If any of the input parameters are invalid.
        APIError: If the API request fails or returns an error response.
    """
    # Validate parameters
    if not (0 <= stability <= 1):
        raise ValidationError("Stability must be between 0 and 1")
    if not (0 <= similarity_boost <= 1):
        raise ValidationError("Similarity boost must be between 0 and 1")
    if not (0 <= style <= 1):
        raise ValidationError("Style must be between 0 and 1")
    if not text_to_speak:
        raise ValidationError("Text to speak cannot be empty")
    if speed is not None and model_id != "eleven_multilingual_v2":
        raise ValidationError(
            "Speed parameter is only supported for multilingual v2 model"
        )
    if speed is not None and not (0.5 <= speed <= 2.0):
        raise ValidationError("Speed must be between 0.5 and 2.0")

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": xi_api_key, "Content-Type": "application/json"}

    payload: Dict[str, Union[str, int, Dict[str, Union[float, bool]]]] = {
        "text": text_to_speak,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
        },
    }

    if speed is not None and model_id == "eleven_multilingual_v2":
        payload["voice_settings"]["speed"] = speed
    if seed is not None:
        payload["seed"] = seed
    if language_code:
        payload["language_code"] = language_code

    logging.info(
        "Sending request to ElevenLabs API with payload: %s",
        json.dumps(payload, indent=2),
    )

    try:
        response = requests.post(tts_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        response_seed = response.headers.get("x-seed")
        logging.info("Audio generated successfully with seed: %s", response_seed)

        return True, response_seed

    except requests.exceptions.RequestException as e:
        raise APIError("Failed to generate audio", str(e))


def generate_voice_previews(
    api_key: str, voice_description: str
) -> Optional[Dict[str, Any]]:
    """Generate voice previews from description.

    Args:
        api_key (str): ElevenLabs API key for authentication.
        voice_description (str): Description of the desired voice characteristics.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing preview information including:
            - generated_voice_id: ID of the generated voice
            - audio: List of dictionaries with preview IDs and file paths
            Returns None if generation fails.

    Raises:
        ValidationError: If the voice description is empty.
        APIError: If the API request fails or returns an error response.
    """
    if not voice_description:
        raise ValidationError("Voice description cannot be empty")

    url = "https://api.elevenlabs.io/v1/text-to-voice/create-previews"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

    sample_text = """Hello! I'm excited to demonstrate my voice capabilities. 
    I can speak clearly and naturally, adapting my tone to different contexts. 
    Whether it's casual conversation, professional presentations, or storytelling, 
    I aim to deliver high-quality, engaging audio that meets your needs. 
    How can I help bring your content to life today?"""

    payload = {"text": sample_text, "voice_description": voice_description}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        processed_previews = []
        for idx, preview in enumerate(result["previews"]):
            audio_data = base64.b64decode(preview["audio_base_64"])
            preview_path = f"preview_{idx}.mp3"
            with open(preview_path, "wb") as f:
                f.write(audio_data)
            processed_previews.append(
                {"id": preview["generated_voice_id"], "path": preview_path}
            )

        return {
            "generated_voice_id": result["previews"][0]["generated_voice_id"],
            "audio": processed_previews,
        }
    except requests.exceptions.RequestException as e:
        raise APIError("Failed to generate voice previews", str(e))


def create_voice_from_preview(
    api_key: str,
    voice_name: str,
    voice_description: str,
    generated_voice_id: str,
    played_ids: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Create voice from preview.

    Args:
        api_key (str): ElevenLabs API key for authentication.
        voice_name (str): Name for the new voice.
        voice_description (str): Description of the voice characteristics.
        generated_voice_id (str): ID of the generated preview voice to use.
        played_ids (Optional[List[str]], optional): List of played preview IDs. Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: Response data from the API if successful, None if failed.

    Raises:
        ValidationError: If any required parameters are empty.
        APIError: If the API request fails or returns an error response.
    """
    if not voice_name:
        raise ValidationError("Voice name cannot be empty")
    if not voice_description:
        raise ValidationError("Voice description cannot be empty")
    if not generated_voice_id:
        raise ValidationError("Generated voice ID cannot be empty")

    url = "https://api.elevenlabs.io/v1/text-to-voice/create-voice-from-preview"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "voice_name": voice_name,
        "voice_description": voice_description,
        "generated_voice_id": generated_voice_id,
        "labels": {"language": "en"},
        "played_not_selected_voice_ids": played_ids if played_ids else [],
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIError("Failed to create voice from preview", str(e))


def process_text(text: str) -> Tuple[str, List[str]]:
    """Process text to handle variables and preserve formatting.

    Args:
        text (str): Input text to process.

    Returns:
        Tuple[str, List[str]]: Tuple containing:
            - Processed text with newlines preserved
            - List of variable names found in the text
    """
    text = text.replace("\\n", "\n")
    variables = re.findall(r"\{(\w+)\}", text)
    return text, variables


def bulk_generate_audio(
    api_key: str,
    model_id: str,
    voice_id: str,
    csv_file: BinaryIO,
    output_dir: str,
    voice_settings: Dict[str, Any],
    seed_type: str,
    seed: Optional[int] = None,
) -> Tuple[bool, str]:
    """Generate audio in bulk from CSV file.

    Args:
        api_key (str): ElevenLabs API key for authentication.
        model_id (str): ID of the model to use.
        voice_id (str): ID of the voice to use.
        csv_file (BinaryIO): CSV file object containing text and filename columns.
        output_dir (str): Directory to save generated audio files.
        voice_settings (Dict[str, Any]): Dictionary containing voice generation settings.
        seed_type (str): Type of seed to use for generation.
        seed (Optional[int], optional): Fixed seed value. Defaults to None.

    Returns:
        Tuple[bool, str]: Tuple containing:
            - Success status
            - Status message or error description

    Raises:
        ValidationError: If the CSV file format is invalid.
        APIError: If the API request fails or returns an error response.
    """
    try:
        csv_file.seek(0)
        df = pd.read_csv(csv_file)

        if "text" not in df.columns:
            raise ValidationError(
                "CSV must contain 'text' column",
                "Please ensure your CSV file has a column named 'text'",
            )

        os.makedirs(output_dir, exist_ok=True)

        for index, row in df.iterrows():
            text = row["text"]
            filename = f"{row.get('filename', f'audio_{index}')}.mp3"
            output_path = os.path.join(output_dir, filename)

            current_seed = (
                random.randint(0, 9999999999) if seed_type == "Random" else seed
            )

            # Cast voice settings to correct types
            stability = float(voice_settings["stability"])
            similarity_boost = float(voice_settings["similarity_boost"])
            style = float(voice_settings["style"])
            use_speaker_boost = bool(voice_settings["use_speaker_boost"])
            # Extract speed if present, otherwise default to None
            speed_value = voice_settings.get("speed")
            if speed_value is not None:
                speed_value = float(speed_value)

            success, response_seed = generate_audio(
                api_key,
                stability,
                model_id,
                similarity_boost,
                style,
                use_speaker_boost,
                voice_id,
                text,
                output_path,
                seed=current_seed,
                speed=speed_value,  # Pass speed here
            )

            if not success:
                raise APIError(f"Failed to generate audio for row {index}")

        return True, "Bulk generation completed successfully"

    except Exception as e:
        raise APIError("Failed to process bulk generation", str(e))
