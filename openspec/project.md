# ElevenTools Project Context

## Purpose
ElevenTools is a comprehensive interface for ElevenLabs' text-to-speech API, designed to streamline the process of generating high-quality voice content. It provides both single and bulk generation capabilities, with advanced features for customization, reproducibility, and variable replacement. The application emphasizes user-friendliness, flexibility, reproducibility (through seed management), and extensibility.

## Core Principles
1. **User-Friendly:** Intuitive interface for both novice and experienced users
2. **Flexibility:** Support for various use cases, from single audio clips to large-scale batch processing
3. **Reproducibility:** Emphasis on seed management for consistent results
4. **Extensibility:** Modular design to easily incorporate new features and integrations
5. **Cloud-Ready:** Designed to run seamlessly in cloud environments with secure API key management

## Tech Stack

### Core Technologies
- **Frontend:** Streamlit (Python-based web framework)
- **Backend/Core Logic:** Python 3.12+
- **Package Manager:** `uv` (fast Python package and environment manager)
- **APIs:**
  - ElevenLabs (Text-to-Speech, voice generation)
  - OpenRouter (for translations and phonetic conversions)
- **Testing:** pytest, unittest.mock, streamlit-testing

### Key Python Packages
- `streamlit>=1.32.0` - Web framework
- `elevenlabs>=0.3.0` - TTS API integration
- `openai>=1.12.0` - OpenAI API for OpenRouter integration
- `pandas>=2.2.3` - Data handling for CSV processing
- `requests>=2.31.0` - HTTP requests
- `pydantic>=2.6.0` - Data validation

## Project Conventions

### Code Style
- Follow PEP8 and Python best practices
- Use type hints for all function parameters and return values
- Write clear, well-documented code with docstrings
- Keep business logic separate from UI code (Streamlit presentation logic)
- Use meaningful variable and function names
- Separate concerns: API calls in `scripts/`, UI in `pages/`
- Code formatting: Black for auto-formatting

### Architecture Patterns

**Modular Design:**
- UI components in `pages/` directory (Streamlit multipage app structure)
  - Main page (`app.py`): Advanced text-to-speech interface
  - Voice Design page: Voice creation and customization
  - Bulk Generation page: Batch processing of audio files
  - Translation page: Script translation capabilities
  - Settings page: Secure API key management and default model configuration
  - File Explorer page: Generated audio management
- Business logic in `scripts/` directory organized by domain
  - `Elevenlabs_functions.py` - ElevenLabs API integration
  - `openrouter_functions.py` - OpenRouter API integration
  - `Translation_functions.py` - Translation capabilities
  - `functions.py` - Core utilities and helpers
- Utilities and helpers in `utils/` directory for caching, error handling

**Session State Management:**
- Use `st.session_state` for global settings and user session data
- Session-based API key storage for secure cloud deployment
- Never store sensitive data permanently in session state
- Initialize session state variables with clear defaults

**API Integration Patterns:**
- All external API calls must have proper error handling
- Use try-catch blocks with user-friendly error messages
- Cache API results where appropriate (`@st.cache_data` for data, `@st.cache_resource` for connections)
- Mock all external API calls in tests
- Session-based API key management for multi-user cloud environments

**Secrets Management:**
- Use `st.secrets` for all API keys and sensitive configuration during development
- Session-based API key storage for production cloud deployment
- Never hardcode secrets or credentials
- Structure secrets hierarchically in `.streamlit/secrets.toml`

### Testing Strategy

**Test Organization:**
- Tests mirror source structure (`tests/api/`, `tests/web/`, etc.)
- Unit tests for core functions
- Integration tests for API interactions
- UI tests using `streamlit-testing` framework

**Test Requirements:**
- Mock all external API calls (ElevenLabs, OpenRouter, Ollama)
- Cover both success and failure modes
- Test edge cases and error handling
- Use fixtures for shared test setup
- All new features must include corresponding tests

**Test Execution:**
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_api/test_elevenlabs_functions.py

# Run with verbose output
uv run pytest -v
```

### Git Workflow

**Branching Model:**
- `main`: Production branch, always stable and deployable
- `develop`: Ongoing development branch for features and bugfixes
- `cloud`: Experimental or cloud-specific features branch

**Development Workflow:**
- Use feature branches for development
- Keep PRs focused and well-documented
- Push to GitHub repo each time a subtask is marked as done
- Never force push to main or develop branches

**Commit Conventions:**
- Clear, descriptive commit messages
- Reference task IDs when applicable (e.g., `[T123] Implement feature X`)
- Separate commits for different logical changes

## Domain Context

### Core Capabilities

**1. Text-to-Speech Generation**
- Single audio generation with immediate playback
- Advanced voice settings (stability, similarity, style, speaker boost, speed)
- Seed management for reproducible results
- Variable replacement for personalized content
- Support for multiple ElevenLabs models (monolingual v1, multilingual v2)

**2. Voice Design & Management**
- Voice generation from text descriptions
- AI-powered prompt enhancement via OpenRouter
- Voice preview system with multiple variations
- Voice ID management and copying functionality
- Real-time voice characteristic controls

**3. Bulk Audio Generation**
- CSV file upload for batch processing
- Support for text variables in CSV columns
- Random or fixed seed options across batches
- Parallel generation for improved performance
- Variable detection and validation
- CSV editor for creating properly formatted files

**4. Translation & Localization**
- Multi-language script translation via OpenRouter
- Phonetic conversion support
- Integration with text-to-speech workflow

**5. File Management**
- Consolidated file explorer for all generated audio
- Organized output structure (single vs bulk outputs)
- File naming convention: `LANGUAGE_VOICE_NAME_DATE_ID_SEED.mp3`
- Bulk outputs grouped by source CSV file
- Audio playback and metadata display

### API Integrations

**ElevenLabs API**
- Text-to-speech synthesis
- Voice library management  
- Voice generation from descriptions
- Audio format and quality control

**OpenRouter API**
- Language translation services
- Phonetic conversions
- AI-powered prompt enhancement for voice design
- Configurable model selection (default: "openrouter/auto")

### File Organization Structure
- Single outputs: `outputs/single/` 
- Bulk outputs: `outputs/{CSV_FILENAME}/`
- File naming: `LANGUAGE_VOICE_NAME_DATE_ID_SEED.mp3`
- Consolidated file explorer with metadata tracking

## Important Constraints

### Security Requirements
- **CRITICAL**: Never hardcode secrets or API keys in source code
- Always use `.streamlit/secrets.toml` for sensitive configuration
- Use `enforceSerializableSessionState = true` in production config
- Validate all user inputs before processing
- Secure API key management for multi-user cloud deployment

### Performance Requirements
- Cache API results with `@st.cache_data` (data operations) and `@st.cache_resource` (models/connections)
- Limit DataFrame sizes (max 1000 rows for display)
- Show progress bars for operations > 1 second
- Optimize bulk generation for large datasets

### Package Management
- **MANDATORY**: Use `uv` for all package management
- Never use `pip` directly - use `uv add`, `uv remove`, `uv sync`
- Pin dependency versions in `pyproject.toml`
- Document dependency rationale in comments
- Run `uv audit` regularly for security

### Task Management
- All tasks tracked using OpenSpec change proposals in `openspec/changes/`
- Each change proposal includes `tasks.md` with implementation checklist
- Use unique verb-led change IDs (e.g., `add-feature-name`, `fix-issue-name`)
- Mark completed tasks with `[x]` in `tasks.md`
- Break tasks with complexity > 5/10 into subtasks
- Explicitly list task dependencies
- See `openspec/AGENTS.md` for OpenSpec workflow guidelines

### Design Alignment
- All features must align with OpenSpec specifications in `openspec/specs/`
- Specifications define requirements and scenarios for each capability
- **PERMISSION REQUIRED**: Never modify specs without going through OpenSpec change proposal process
- Create change proposals in `openspec/changes/<change-id>/` for spec modifications
- Include `design.md` in change proposals for architectural decisions or complex changes
- For ambiguities, ask for clarification before coding

## External Dependencies

### ElevenLabs API
- **Purpose:** Text-to-speech synthesis, voice generation, voice preview
- **Key Endpoints:**
  - Text-to-Speech generation
  - Voice library management
  - Voice generation from descriptions
- **Authentication:** API key via `st.secrets["ELEVENLABS_API_KEY"]`
- **Rate Limits:** Depends on ElevenLabs plan
- **Error Handling:** Required for all API calls with user-friendly messages

### OpenRouter API
- **Purpose:** Language translation, phonetic conversions, prompt enhancement
- **Model:** "openrouter/auto" (default, configurable)
- **Authentication:** API key via `st.secrets["OPENROUTER_API_KEY"]`
- **Error Handling:** Comprehensive with retry logic for transient failures

### Ollama (Local)
- **Purpose:** Local LLM for voice design enhancements
- **Model:** llama3.2:3b
- **Requirement:** Ollama must be installed and running locally
- **Usage:** Voice description prompt enhancement
- **Setup:** `ollama pull llama3.2:3b` then ensure service is running

### Test Dependencies
- `pytest>=8.0.0` - Test framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `unittest.mock` - Mocking framework for tests
- `streamlit-testing` - Streamlit app testing

### Development Dependencies
- `black>=24.0.0` - Code formatting
- `flake8>=7.0.0` - Linting
- `mypy>=1.8.0` - Type checking
- `isort>=5.13.0` - Import sorting
