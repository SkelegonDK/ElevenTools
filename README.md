# ElevenTools

Eleventools is my personal toolbox for Elevenlabs.
It has all of the bells and whistles I need to get started on a new project.

## Installation

Install Python 3.10 or latest and pipenv if you want

```bash
pip install streamlit, openai
streamlit run app.py
```

## Global secrets and API keys

Create a /.streamlit/secrets.toml file in the root directory with your elevenlabs and openai keys.
Create a /.streamlit/config.toml file in the root directory to set the page settings and colors.

## Features

- Voice selection search through the Elevenlabs library
- Model selection
- Allows for text variables for personalization
- Random and fixed seed for reproducibility
- Voice settings
- review generation data and play audio

## TODO:

- [x] OPENAI INTEGRATION
- [ ] OLLAMA INTEGRATION
- [ ] Batch processing
- [ ] Voice to Voice
- [x] Import user voices automatically
- [ ] Error handling
- [x] Locked or random seed
- [ ] Save generated audio data
