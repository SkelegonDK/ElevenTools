# ElevenTools Alpha v0.0.1

Eleventools is my personal toolbox for Elevenlabs.
It has all of the bells and whistles I need to get started on a new project.

## Installation

Install Python 3.10 or latest and pipenv if you want

```bash
pip install streamlit openai
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

- [ ] OLLAMA INTEGRATION
- [ ] CLAUDE INTEGRATION
- [ ] Batch processing with CSV
- [ ] Voice to Voice
- [ ] Error handling ( mostly done)
- [ ] Save generated audio data
- [ ] Page routing
- [ ] search by voice ID

## DONE:

- [x] FIXED SEED
- [x] OPENAI INTEGRATION
- [x] Import user voices automatically
- [x] Locked or random seed