# Import necessary libraries
import streamlit as st  # Used for building the web app
import requests  # Used for making HTTP requests
import json  # Used for working with JSON data
from pprint import pprint  # Used for pretty-printing JSON data
import logging
import pandas as pd
import os
import re


@st.cache_data(ttl=3600)  # Cache the data for 1 hour
def fetch_models(api_key):
    """
    Fetches the list of available models from the ElevenLabs API.
    """
    url = "https://api.elevenlabs.io/v1/models"
    headers = {"xi-api-key": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        models = response.json()
        return [(model["model_id"], model["name"]) for model in models]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch models: {str(e)}")
        return []


@st.cache_data(ttl=3600)  # Cache the data for 1 hour
def fetch_voices(api_key):
    """
    Fetches the list of available voices from the ElevenLabs API.
    """
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        voices = response.json()["voices"]
        return [(voice["voice_id"], voice["name"]) for voice in voices]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch voices: {str(e)}")
        return []


def get_voice_id(voices, selected_voice_name):
    """
    Get the voice ID for the selected voice name.
    """
    for voice_id, name in voices:
        if name == selected_voice_name:
            return voice_id
    return None  # Return None if no matching voice is found


def generate_audio(
    xi_api_key,
    stability,
    model_id,
    similarity_boost,
    style,
    use_speaker_boost,
    voice_id,
    text_to_speak,
    output_path="output.mp3",
    seed=None,
    language_code=None,
):
    """
    Generate audio using the Elevenlabs Text-to-Speech API.
    """
    # Construct the URL for the Text-to-Speech API request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    # Set up headers for the API request
    headers = {"xi-api-key": xi_api_key, "Content-Type": "application/json"}

    # Set up the data payload for the API request
    payload = {
        "text": text_to_speak,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
        },
    }

    # Add optional parameters if provided
    if seed is not None:
        payload["seed"] = int(seed)
    if language_code:
        payload["language_code"] = language_code

    # Log the payload being sent to the API
    logging.info(
        f"Sending request to ElevenLabs API with payload: {json.dumps(payload, indent=2)}"
    )

    # Make the POST request to the TTS API
    response = requests.post(tts_url, headers=headers, json=payload, timeout=30)

    # Log the full response details
    logging.info(f"API Response Status Code: {response.status_code}")
    logging.info(
        f"API Response Headers: {json.dumps(dict(response.headers), indent=2)}"
    )

    # Check if the request was successful
    if response.ok:
        logging.info("Request to ElevenLabs API was successful")

        # Write the audio content to file
        with open(output_path, "wb") as f:
            f.write(response.content)

        # Check for seed information in the response headers (just in case)
        response_seed = response.headers.get("x-seed")

        if response_seed:
            logging.info(f"Seed found in response headers: {response_seed}")
        else:
            logging.info("No seed found in response headers.")

        # Log the entire response content for debugging
        logging.info(
            f"Full response content: {response.content[:1000]}..."
        )  # Log first 1000 bytes

        st.toast("Audio generated successfully.")
        return (
            True,
            response_seed,
        )  # Indicate success and return the seed from the response (if any)
    else:
        # Log the error message if the request was not successful
        logging.error(f"Error response from ElevenLabs API: {response.text}")
        st.error(f"Failed to generate audio. API response: {response.text}")
        return False, None  # Indicate failure and return None for the seed


### BULK GENERATION FUNCTIONS ###


def process_text(text):
    """
    Process the text to handle variables and preserve formatting.
    """
    # Replace \n with actual newlines
    text = text.replace("\\n", "\n")

    # Handle variables (assuming format like {variable_name})
    variables = re.findall(r"\{(\w+)\}", text)
    return text, variables


def bulk_generate_audio(
    api_key, model_id, voice_id, csv_file, output_dir, voice_settings
):
    try:
        df = pd.read_csv(csv_file, keep_default_na=False)
        results = []

        for index, row in df.iterrows():
            text, variables = process_text(row["text"])

            # Replace variables with their values if provided in the CSV
            for var in variables:
                if var in row:
                    text = text.replace(f"{{{var}}}", str(row[var]))

            filename = (
                f"{row['filename']}.mp3" if "filename" in row else f"audio_{index}.mp3"
            )
            output_path = os.path.join(output_dir, filename)

            success, response_seed = generate_audio(
                api_key,
                voice_settings["stability"],
                model_id,
                voice_settings["similarity_boost"],
                voice_settings["style"],
                voice_settings["speaker_boost"],
                voice_id,
                text,
                output_path,
            )

            results.append(
                {
                    "filename": filename,
                    "text": text,
                    "success": success,
                    "seed": response_seed,
                }
            )

        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"An error occurred during bulk generation: {str(e)}")
        return pd.DataFrame()
