# Import necessary libraries
import streamlit as st  # Used for building the web app
import requests  # Used for making HTTP requests
import json  # Used for working with JSON data
from pprint import pprint  # Used for pretty-printing JSON data


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
    seed="None",
):

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
        "seed": None,
    }
    st.write(data)
    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    # Check if the request was successful
    if response.ok:

        # Open the output file in write-binary mode
        with open(output_path, "wb") as f:
            # Read the response in chunks and write to the file
            st.spinner("Generating audio...")
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        # Inform the user of success
        st.toast("Audio generated successfully.")
    else:
        # Print the error message if the request was not successful
        pprint(response.text)
