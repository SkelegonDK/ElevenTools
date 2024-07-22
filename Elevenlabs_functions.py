# Import necessary libraries
import streamlit as st  # Used for building the web app
import requests  # Used for making HTTP requests
import json  # Used for working with JSON data
from pprint import pprint  # Used for pretty-printing JSON data
import logging


def get_voice_id(voice_library, selected_voice):
    """
    Get the voice ID for the selected voice from the voice library.
    """
    for voice in voice_library:
        if voice["name"] == selected_voice:
            # Check if 'voice_id' key exists in the dictionary
            if "voice_id" in voice:
                return voice["voice_id"]
            else:
                raise KeyError(
                    f"The dictionary does not contain the key 'voice_id': {voice}"
                )
    return None


@st.cache_data(ttl=300)  # Cache the data for 1 hour (3600 seconds)
def fetch_voices(api_key):
    """
    Fetches the list of available voices from the Elevenlabs API.
    """
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()["voices"]
    else:
        st.error("Failed to fetch voices from Elevenlabs API.")
        return []


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
    seed=0,
):
    """
    Generate audio using the Elevenlabs Text-to-Speech API.
    """
    CHUNK_SIZE = 1024  # Size of chunks to read/write at a time

    # Construct the URL for the Text-to-Speech API request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

    # Set up headers for the API request, including the API key for authentication
    headers = {"Accept": "application/json", "xi-api-key": xi_api_key}

    # Set up the data payload for the API request, including the text and voice settings
    data = {
        "text": text_to_speak,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
        },
        "seed": int(seed) if seed else None,
    }

    # Log the payload being sent to the API
    logging.info(
        f"Sending request to ElevenLabs API with payload: {json.dumps(data, indent=2)}"
    )

    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(
        tts_url, headers=headers, json=data, stream=True, timeout=10
    )

    # Log the full response details
    logging.info(f"API Response Status Code: {response.status_code}")
    logging.info(
        f"API Response Headers: {json.dumps(dict(response.headers), indent=2)}"
    )

    # Check if the request was successful
    if response.ok:
        logging.info("Request to ElevenLabs API was successful")
        # Open the output file in write-binary mode
        with open(output_path, "wb") as f:
            # Read the response in chunks and write to the file
            st.spinner("Generating audio...")
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        # Inform the user of success
        st.toast("Audio generated successfully.")
        return True  # Indicate success
    else:
        # Log the error message if the request was not successful
        logging.error(f"Error response from ElevenLabs API: {response.text}")
        try:
            error_json = response.json()
            logging.error(
                f"Detailed error information: {json.dumps(error_json, indent=2)}"
            )
        except json.JSONDecodeError:
            logging.error("Could not parse error response as JSON")
        st.error(f"Failed to generate audio. API response: {response.text}")
        return False  # Indicate failure
