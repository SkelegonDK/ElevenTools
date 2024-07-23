# ElevenTools Alpha v0.1.0

ElevenTools is a comprehensive toolbox for ElevenLabs, providing a user-friendly interface for text-to-speech generation with advanced features and bulk processing capabilities.

## Features

- Dynamic voice and model selection from the ElevenLabs library
- Text variable support for personalized audio generation
- Random and fixed seed options for reproducible results
- Customizable voice settings (stability, similarity, style, speaker boost)
- Single and bulk audio generation
- CSV support for batch processing
- Review and playback of generated audio
- OpenAI integration for phonetic conversions

## Installation

1. Ensure you have Python 3.10 or later installed.
2. Clone this repository:
   ```bash
   git clone https://github.com/your-username/eleventools.git
   cd eleventools
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.streamlit/secrets.toml` file in the root directory with your API keys:
   ```toml
   ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
   OPENAI_API_KEY = "your_openai_api_key"
   ```
2. (Optional) Create a `.streamlit/config.toml` file to customize Streamlit's appearance and behavior.

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Navigate to the provided local URL to access the ElevenTools interface.

## Bulk Generation

1. Prepare a CSV file with columns: 'text', 'filename' (optional), and any variables used in the text.
2. Use the Bulk Generation page to upload your CSV and generate multiple audio files.
3. Choose between random or fixed seed generation for consistent results.

## TODO

- [ ] Implement OLLAMA integration
- [ ] Enhance Voice-to-Voice functionality
  - [ ] Add voice cleanup features
- [ ] Improve data persistence
  - [ ] Save generated audio metadata
  - [ ] Implement pronunciation memory
- [ ] Expand bulk processing capabilities
- [ ] Add search functionality for voice IDs

## License

ElevenTools is open-source software released under a custom license. 

- Free for individual use and for companies with less than $10 million in annual revenue and fewer than 50 employees.
- Commercial licensing required for larger companies.
- Use for training AI models is prohibited without explicit permission.

Please see the [full license](LICENSE) for all terms and conditions.

For commercial licensing inquiries, please contact [your contact information].

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue in this repository.