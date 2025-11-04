# ElevenTools v0.3.0

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
- OpenRouter integration for translations and language processing
- **OpenRouter model selection with fuzzy search** - Discover and select from available OpenRouter models with intelligent search
- **Free model filtering** - Filter to show only zero-cost models for cost-effective translations

## Installation

1. Ensure you have Python 3.12 installed.
2. Install [uv](https://github.com/astral-sh/uv) (a fast Python package/dependency manager):

   ```bash
   curl -Ls https://astral.sh/uv/install.sh | sh
   # or use Homebrew: brew install astral-sh/uv/uv
   ```

3. Sync your environment and install dependencies:

   ```bash
   uv sync
   ```

   To include development dependencies:

   ```bash
   uv sync --extra dev
   ```

## Configuration

ElevenTools supports multiple methods for providing API keys, making it flexible for both local development and cloud deployment:

### API Key Management

#### Method 1: Session-Based Storage (Recommended for Cloud Deployment)

- Navigate to the **Settings** page in the sidebar
- Enter your API keys directly in the interface
- Keys are stored only in your browser session (never saved to disk or shared between users)
- Perfect for multi-user cloud deployments without requiring authentication layers
- Keys persist across page navigations within the same browser session

#### Method 2: Streamlit Secrets (For Streamlit Cloud)

- Configure secrets in your Streamlit Cloud app settings
- See [Streamlit Cloud Secrets Documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- Secrets are shared across all users of the deployed app

#### Method 3: Local secrets.toml (For Local Development)

- Create a `.streamlit/secrets.toml` file in the root directory:

   ```toml
   ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
   OPENROUTER_API_KEY = "your_openrouter_api_key"
   ```

#### Priority Order

1. Session state (user-entered keys via Settings page)
2. Streamlit secrets (cloud dashboard or local secrets.toml)

Both API keys are required for full functionality:

- **ELEVENLABS_API_KEY**: Required for text-to-speech generation
- **OPENROUTER_API_KEY**: Required for translations and OpenRouter model selection features

### Additional Configuration

(Optional) Create a `.streamlit/config.toml` file to customize Streamlit's appearance and behavior.

### Streamlit Cloud Deployment

When deploying to Streamlit Cloud:

1. **Option A**: Configure secrets via the Streamlit Cloud dashboard (shared across all users)
2. **Option B**: Users can enter their own API keys via the Settings page (per-user keys)

The session-based approach allows each user to provide their own API keys without requiring a full authentication layer, making it ideal for prototype and multi-user scenarios.

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
   ollama pull llama3.2:3b
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
uv run -- streamlit run app.py
```

Navigate to the provided local URL to access the ElevenTools interface.

## Bulk Generation

1. Prepare a CSV file with columns: 'text', 'filename' (optional), and any variables used in the text.
2. Use the Bulk Generation page to upload your CSV and generate multiple audio files.
3. Choose between random or fixed seed generation for consistent results.

## Testing

ElevenTools uses pytest for unit testing and Playwright for UI testing. The test suite is comprehensively organized to cover all major components:

### Test Organization

**Unit Tests** (`tests/test_api/`, `tests/test_utils/`, `tests/test_web/`):

- `test_elevenlabs_functions.py`: Tests for ElevenLabs API interactions
- `test_openrouter_functions.py`: Tests for OpenRouter API integration
- `test_openrouter_model_functions.py`: Tests for model fetching, filtering, and fuzzy search
- `test_functions.py`: Tests for utility functions
- `test_streamlit_pages.py`: Tests for Streamlit page components
- `test_file_explorer.py`: Tests for file management functionality

**UI Tests** (`tests/ui_tests/`):

- `test_main_page.py`: Playwright tests for main TTS interface
- `test_translation_page.py`: Playwright tests for translation page with model selection
- `test_bulk_generation_page.py`: Playwright tests for bulk generation
- `test_file_explorer_page.py`: Playwright tests for file explorer
- `test_settings_page.py`: Playwright tests for Settings page

### Running Tests

1. Ensure dev dependencies are installed (includes Playwright):

   ```bash
   uv sync --extra dev
   ```

2. Install Playwright browsers (first time only):

   ```bash
   uv run playwright install
   ```

3. Run all tests:

   ```bash
   uv run pytest
   ```

4. Run only unit tests:

   ```bash
   uv run pytest tests/test_api/ tests/test_utils/ tests/test_web/
   ```

5. Run only UI tests:

   ```bash
   uv run pytest tests/ui_tests/
   ```

6. Run tests for a specific file:

   ```bash
   uv run pytest tests/test_api/test_openrouter_model_functions.py
   ```

7. Run tests with verbose output:

   ```bash
   uv run pytest -v
   ```

8. Run UI tests with headed browser (see what's happening):

   ```bash
   uv run pytest tests/ui_tests/ --headed
   ```

When contributing new features or making changes, please add or update the relevant tests to ensure code quality and prevent regressions. All new features should include both unit tests and UI tests where applicable.

## Project Management

ElevenTools uses **OpenSpec** for task management and spec-driven development. All change proposals, specifications, and tasks are tracked in the `openspec/` directory.

## Current Development Status

### Recently Completed Features

- ✅ **Comprehensive testing suite** - Unit tests and Playwright UI tests covering all major components
- ✅ **Ollama integration** - Local language model processing for voice design enhancements
- ✅ **OpenRouter model selection** - Fuzzy search and free model filtering for translation customization
- ✅ **API response caching** - Model fetching and other API calls use Streamlit caching for performance

### Active Development

Current change proposals and specifications can be viewed with:

```bash
openspec list
openspec list --specs
```

To view details of a specific change:

```bash
openspec show <change-id>
```

For more information about OpenSpec and the project structure, see `openspec/AGENTS.md`.

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

## Voice Settings

The following voice settings can be adjusted:

- **Stability** (0.0-1.0): Controls the stability of the voice. Higher values make the voice more consistent.
- **Similarity Boost** (0.0-1.0): Controls how closely the voice matches the reference audio.
- **Style** (0.0-1.0): Controls the expressiveness of the voice.
- **Speaker Boost**: Enhances the clarity and presence of the speaker's voice.
- **Speed** (0.5-2.0): Controls the speaking speed (only available with multilingual v2 model)
  - 0.5: Half speed
  - 1.0: Normal speed (default)
  - 2.0: Double speed

## Models

### ElevenLabs Models

The following ElevenLabs models are available:

- **Monolingual v1**: English-only model optimized for speed
- **Multilingual v2**: Advanced model supporting multiple languages and speed control

### OpenRouter Models

For translation and language processing, ElevenTools integrates with OpenRouter, providing access to a wide variety of language models:

- **Model Selection**: Browse and search through available OpenRouter models with fuzzy search
- **Free Model Filtering**: Filter to show only zero-cost models for cost-effective translations
- **Real-time Search**: Search models by name with support for partial matches and typos
- **Default Model**: Uses "openrouter/auto" by default, but you can select any available model

## Branching Model

- **main**: Production branch, always stable and deployable. All releases are tagged from here.
- **develop**: Ongoing development branch. All new features and bugfixes are merged here before going to main.
- **cloud**: Experimental or cloud-specific features branch, based on develop.

**Recent update:**

- `main` was updated to match `develop` (June 2024).
- `cloud` branch created from `develop` for cloud-specific work.
