# ElevenTools

Eleventools is my personal toolbox for Elevenlabs. 
It has all of the bells and whistles I need to get started on a new project.

## Installation

Install Python 3.10 or latest and pipenv if you want

```bash
pip install streamlit, openai
streamlit run app.py
```

## Global secrets

Create a /.streamlit/secrets.toml file in the root directory with your elevenlabs and openai keys.
Create a /.streamlit/config.toml file in the root directory to set the page settings and colors.

## Features

- Voice selection ( copy paste the voice ID from the Voice library)
- Copy paste the voice ID fromthe Voice library
- Model selection:
- Allows for text variables for personalization
- Random and fixed seed for reproducibility
- Voice settings

## TODO:

- [x] OPENAI INTEGRATION
- [ ] OLLAMA INTEGRATION
- [ ] Batch processing
- [ ] Voice to Voice
- [ ] Import user voices
- [ ] Error handling
- [x] Locked or random seed
