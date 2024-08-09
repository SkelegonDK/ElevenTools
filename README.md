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
- Ollama integration for local language model processing

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

1. Create a `.streamlit/secrets.toml` file in the root directory with your API key:
   ```toml
   ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
   ```
2. (Optional) Create a `.streamlit/config.toml` file to customize Streamlit's appearance and behavior.

## Ollama Setup

ElevenTools integrates with Ollama for local language model processing. To use this feature, you need to install Ollama and download the appropriate model:

1. Install Ollama:
   - For macOS and Linux:
     ```bash
     curl https://ollama.ai/install.sh | sh
     ```
   - For Windows:
     Download and install from [Ollama's official website](https://ollama.ai/download)

2. Download the required model:
   After installing Ollama, open a terminal and run:
   ```bash
   ollama pull llama3.1:8b
   ```
   This will download the small and efficient Llama 3.1:8b model, which is currently used by ElevenTools.

3. Ensure Ollama is running:
   Ollama should start automatically after installation. If it's not running, you can start it manually:
   - On macOS/Linux: `ollama serve`
   - On Windows: Run the Ollama application

For more information on Ollama, visit [ollama.ai](https://ollama.ai).

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

## Testing

ElevenTools uses pytest for testing. The test suite is organized into separate files for each main component of the application:

- `test_functions.py`: Tests for utility functions in `functions.py`
- `test_elevenlabs_functions.py`: Tests for ElevenLabs API interactions in `Elevenlabs_functions.py`
- `test_ollama_functions.py`: Tests for Ollama integration in `ollama_functions.py`
- `test_streamlit_pages.py`: Tests for Streamlit pages (Home.py and Bulk_Generation.py)

To run the tests:

1. Install pytest if you haven't already:
   ```bash
   pip install pytest
   ```

2. Run all tests:
   ```bash
   pytest
   ```

3. To run tests for a specific file:
   ```bash
   pytest test_functions.py
   ```

4. To run tests with more detailed output:
   ```bash
   pytest -v
   ```

5. To run tests and see print statements:
   ```bash
   pytest -s
   ```

When contributing new features or making changes, please add or update the relevant tests to ensure code quality and prevent regressions.

# TODO List for Eleven Tools

## High Priority
1. ~~Implement automated testing~~
   - [x] Unit tests for core functions
   - [x] Integration tests for API interactions
   - [x] End-to-end tests for user workflows

2. Integrate OLLAMA
   - [x] Implement OLLAMA integration in the codebase
   - [x] Create tests for OLLAMA integration
   - [ ] Test and improve enhancing process

3. Enhance UI/UX
   - [ ] Implement progress bars for audio generation
   - [ ] Improve error messaging and user feedback
   - [ ] Create a more intuitive layout for voice settings

4. Optimize performance
   - [ ] Implement caching for frequently used data
   - [ ] Optimize bulk generation for large datasets

5. Security enhancements
   - [ ] Implement proper API key management
   - [ ] Add user authentication for multi-user support

## Medium Priority
6. Improve data management
   - [ ] Implement a database for storing generation history
   - [ ] Create export options for generated audio metadata
   - [ ] Develop a pronunciation memory system

7. Expand features
   - [ ] Add search functionality for voice IDs

8. Documentation
   - [ ] Create comprehensive API documentation
   - [ ] Develop a user guide with examples and best practices

## Lower Priority
9. Enhance Voice-to-Voice functionality
   - [ ] Add voice cleanup features

10. UI/UX improvements (continued)
    - [ ] Implement a dark mode option

## Grouped by Feature Area

### Testing and Quality Assurance
- ~~Implement automated testing~~
  - [x] Unit tests for core functions
  - [x] Integration tests for API interactions
  - [x] End-to-end tests for user workflows

### OLLAMA Integration
- Integrate OLLAMA
  - [x] Research OLLAMA API and integration requirements
  - [x] Design integration architecture
  - [x] Implement OLLAMA integration in the codebase
  - [x] Create tests for OLLAMA integration
  - [ ] Test and improve enhancing process

### User Interface and Experience
- Enhance UI/UX
  - [ ] Implement progress bars for audio generation
  - [ ] Improve error messaging and user feedback
  - [ ] Create a more intuitive layout for voice settings
  - [ ] Implement a dark mode option

### Performance and Optimization
- Optimize performance
  - [ ] Implement caching for frequently used data
  - [ ] Optimize bulk generation for large datasets

### Security
- Security enhancements
  - [ ] Implement proper API key management
  - [ ] Add user authentication for multi-user support

### Data Management and Persistence
- Improve data management
  - [ ] Implement a database for storing generation history
  - [ ] Create export options for generated audio metadata
  - [ ] Develop a pronunciation memory system

### Feature Expansion
- Expand features
  - [ ] Add search functionality for voice IDs
- Enhance Voice-to-Voice functionality
  - [ ] Add voice cleanup features

### Documentation
- Documentation
  - [ ] Create comprehensive API documentation
  - [ ] Develop a user guide with examples and best practices

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