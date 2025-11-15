# ElevenTools v0.3.0

[![CI/CD Pipeline](https://github.com/SkelegonDK/ElevenTools/actions/workflows/ci.yml/badge.svg)](https://github.com/SkelegonDK/ElevenTools/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/SkelegonDK/ElevenTools/branch/main/graph/badge.svg)](https://codecov.io/gh/SkelegonDK/ElevenTools)
[![License](https://img.shields.io/badge/license-Custom-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.32+-red.svg)](https://streamlit.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

ElevenTools is a comprehensive toolbox for ElevenLabs, providing a user-friendly interface for text-to-speech generation with advanced features and bulk processing capabilities.

> 📝 **Note**: See [CHANGELOG.md](CHANGELOG.md) for version history and recent updates.

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
- **Dynamic model capability detection** - Automatically detects which voice settings each ElevenLabs model supports, adapting UI controls and validation dynamically

## Screenshots

### Main Interface
![Main Interface](docs/screenshots/main-interface.png)
*The main text-to-speech generation interface with voice and model selection*

### Bulk Generation
![Bulk Generation](docs/screenshots/bulk-generation.png)
*CSV-based bulk audio generation with variable replacement*

### Settings Page
![Settings](docs/screenshots/settings.png)
*Secure API key management and configuration*

### File Explorer
![File Explorer](docs/screenshots/file-explorer.png)
*Browse and download generated audio files organized by session*

> **Note**: Screenshots are placeholders. Add actual screenshots to `docs/screenshots/` directory.

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

## Deployment

ElevenTools can be deployed in several ways depending on your needs:

### Streamlit Cloud Deployment

Streamlit Cloud is the easiest way to deploy ElevenTools:

1. **Connect your repository** to [Streamlit Cloud](https://streamlit.io/cloud)
2. **Configure secrets** (optional):
   - Go to your app settings in Streamlit Cloud
   - Add secrets via the dashboard (shared across all users)
   - See [Streamlit Cloud Secrets Documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
3. **Deploy**: Streamlit Cloud will automatically detect and deploy your app

**API Key Options:**
- **Option A**: Configure secrets via the Streamlit Cloud dashboard (shared across all users)
- **Option B**: Users can enter their own API keys via the Settings page (per-user keys)

The session-based approach allows each user to provide their own API keys without requiring a full authentication layer, making it ideal for prototype and multi-user scenarios.

### Docker Deployment

#### Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SkelegonDK/ElevenTools.git
   cd ElevenTools
   ```

2. **Build and run**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Open http://localhost:8501 in your browser

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Stop the application**:
   ```bash
   docker-compose down
   ```

#### Using Docker directly

1. **Build the image**:
   ```bash
   docker build -t eleventools .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     -p 8501:8501 \
     -v $(pwd)/outputs:/app/outputs \
     --name eleventools \
     eleventools
   ```

3. **Access the application**:
   - Open http://localhost:8501 in your browser

### Environment Variables

The following environment variables can be configured:

| Variable | Description | Default |
|----------|-------------|---------|
| `STREAMLIT_SERVER_PORT` | Port for Streamlit server | `8501` |
| `STREAMLIT_SERVER_ADDRESS` | Address to bind to | `0.0.0.0` |
| `SESSION_CLEANUP_TIMEOUT_HOURS` | Hours before session cleanup | `24` |

### Health Checks

The application includes health check endpoints:

- **Health endpoint**: `http://localhost:8501/_stcore/health`
- Docker health checks are configured automatically
- Use this endpoint for load balancer health checks

### Production Considerations

- **API Keys**: Use session-based storage or Streamlit secrets for secure key management
- **File Storage**: Mount persistent volumes for `outputs/` directory in Docker deployments
- **Session Cleanup**: Configure `SESSION_CLEANUP_TIMEOUT_HOURS` based on your usage patterns
- **Resource Limits**: Set appropriate memory and CPU limits for Docker containers
- **Reverse Proxy**: Use nginx or similar for SSL termination and domain routing

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

## File Management

ElevenTools uses **session-based file organization** to ensure privacy and isolation between users, especially important for multi-user cloud deployments.

### Session-Based Storage

- **Session Isolation**: Each user session gets a unique directory (`outputs/{session_id}/`) for their generated files
- **Privacy**: Files from other users' sessions are not accessible
- **Persistence**: Your session ID persists across page navigations within the same browser session
- **Organization**: Files are organized into `single/` and `bulk/` subdirectories within your session directory

### Download Functionality

- **Individual Downloads**: Download any generated audio file directly from the File Explorer or main page audio history
- **Bulk Downloads**: Download all files from your session as a ZIP archive
- **File Explorer**: Browse and download files organized by generation type (single vs bulk)

### Automatic Cleanup

- **Session Timeout**: Session directories older than 24 hours are automatically cleaned up
- **Storage Management**: Prevents storage accumulation in cloud deployments
- **Configurable**: Cleanup timeout can be configured via environment variables
- **Logging**: Cleanup operations are logged for debugging and monitoring

### Migration Notes

If you're upgrading from an older version that used shared `outputs/single/` and `outputs/bulk/` directories:

- **Existing Files**: Old files in the shared directories will remain accessible but won't be automatically migrated
- **New Files**: All new files will be stored in session-specific directories
- **Cleanup**: Old shared directories can be manually removed after verifying no important files remain

## Testing

ElevenTools uses a **curated pytest core suite** (capped below 100 tests) plus optional extended/legacy tests. Core coverage focuses on high-impact API flows, utilities, and Streamlit pages; extended suites include legacy unit coverage and Playwright UI automation. See `docs/testing-core-suite.md` for the scenario catalog and guardrails.

### Test Organization

**Core Suite** (`@pytest.mark.core_suite`)

- `tests/test_api/test_elevenlabs_core.py`
- `tests/test_api/test_openrouter_core.py`
- `tests/test_utils/test_core_utilities.py`
- `tests/test_web/test_pages_core.py`

**Extended Tests**

- Legacy pytest modules under `tests/test_api/`, `tests/test_utils/`, and `tests/test_web/` (no `core_suite` marker)
- Playwright UI tests under `tests/ui_tests/`

### Running Tests

1. Ensure dev dependencies are installed (includes Playwright tooling if you need UI tests):

   ```bash
   uv sync --extra dev
   ```

2. Install Playwright browsers (first time only):

   ```bash
   uv run playwright install
   ```

3. Run the curated core suite (default behaviour):

   ```bash
   uv run pytest
   ```

4. Enforce the `<100` core-suite guardrail (CI must run this):

   ```bash
   uv run python scripts/check_core_suite.py
   ```

5. Run extended pytest suites (legacy + core):

   ```bash
   uv run pytest -m "core_suite or extended"
   ```

6. Run a specific core test file:

   ```bash
   uv run pytest tests/test_api/test_elevenlabs_core.py
   ```

7. Run UI automation (Playwright):

   ```bash
   uv run pytest tests/ui_tests/
   ```

8. Run any pytest command with verbose output:

   ```bash
   uv run pytest -v
   ```

### Testing Standards

When contributing new features or making changes, please follow these testing standards:

#### Test Requirements

- **All new features must include tests** - Both unit tests and UI tests where applicable
- **Test coverage** - Aim for comprehensive coverage of core functionality
- **Test isolation** - Each test should be independent and not rely on execution order
- **Mock external dependencies** - Use `pytest-mock` for mocking API calls and external services

#### Test Patterns

**Unit Tests:**
- Use descriptive test names: `test_<function_name>_<scenario>()`
- Follow Arrange-Act-Assert pattern
- Test one thing per test function
- Use fixtures for reusable setup (`conftest.py`)
- Mock external dependencies (APIs, file system, etc.)

**UI Tests:**
- Use Playwright for end-to-end UI testing
- Test user workflows, not just page loads
- Use explicit waits instead of fixed sleeps
- Test error states and edge cases

**Example Test Structure:**
```python
def test_function_name_scenario(mocker):
    """Test description explaining what is being tested."""
    # Arrange: Set up test data and mocks
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "success"}
    
    # Act: Execute the function being tested
    result = function_under_test(mock_response)
    
    # Assert: Verify the results
    assert result == "success"
```

#### Test Organization

- **One test file per module** - `test_<module_name>.py` for `utils/<module_name>.py`
- **Group related tests** - Use test classes for related functionality
- **Use fixtures** - Create reusable fixtures in `conftest.py`
- **Document tests** - Add docstrings explaining test purpose

#### Mocking Standards

- **Use `pytest-mock`** - Standardize on `mocker` fixture for all tests
- **Mock external APIs** - Never make real API calls in tests
- **Use fixtures for mock data** - Create reusable mock response fixtures
- **Test error paths** - Mock error scenarios (network errors, API errors)

#### Coverage Priorities

1. **P0 (Critical):** Security-critical functions, error handling, core API functions
2. **P1 (High):** User-facing features, core workflows, utility functions
3. **P2 (Medium):** Edge cases, performance optimizations, integration tests
4. **P3 (Low):** Nice-to-have features, accessibility tests, cross-browser tests

For detailed testing patterns and best practices, see `openspec/changes/review-test-suite/TEST_PATTERNS_GUIDE.md`.

### Test Coverage Status

Current test coverage includes:
- ✅ API function tests (ElevenLabs, OpenRouter)
- ✅ Utility function tests (security, session management, API keys)
- ✅ UI tests for major pages (main, translation, bulk generation, file explorer, settings)
- ⚠️ Some areas need additional coverage (see `openspec/changes/review-test-suite/` for detailed analysis)

When adding new tests, refer to existing test files for patterns and conventions.

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

For commercial licensing inquiries, please contact [@SkelegonDK](https://github.com/SkelegonDK) or open an issue in this repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

For detailed guidelines on contributing, including development setup, code style, and testing requirements, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Support

If you encounter any problems or have any questions, please open an issue in this repository.

## Voice Settings

The following voice settings can be adjusted:

- **Stability** (0.0-1.0): Controls the stability of the voice. Higher values make the voice more consistent.
- **Similarity Boost** (0.0-1.0): Controls how closely the voice matches the reference audio.
- **Style** (0.0-1.0): Controls the expressiveness of the voice.
- **Speaker Boost**: Enhances the clarity and presence of the speaker's voice.
- **Speed** (0.5-2.0): Controls the speaking speed (automatically shown/hidden based on selected model capabilities)
  - 0.5: Half speed
  - 1.0: Normal speed (default)
  - 2.0: Double speed
  - The speed control is dynamically displayed only for models that support speed adjustment (e.g., multilingual v2, turbo v2.5, flash v2.5, v3)

## Models

### ElevenLabs Models

The following ElevenLabs models are available:

- **Monolingual v1**: English-only model optimized for speed
- **Multilingual v2**: Advanced model supporting multiple languages and speed control
- **Turbo v2.5**: Fast multilingual model with speed control support
- **Flash v2.5**: Ultra-fast multilingual model with speed control support
- **v3**: Latest generation model with enhanced capabilities

**Dynamic Capability Detection**: ElevenTools automatically detects which voice settings each model supports. The UI adapts dynamically - for example, the speed slider only appears for models that support speed adjustment. This ensures compatibility with new models without requiring code updates.

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
