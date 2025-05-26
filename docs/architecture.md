# ElevenTools Architecture

> **Important Directive:**
>
> Do not assume details about the tech stack. If any aspect of the stack, environment, or workflow is not completely clear, always ask for human feedback and clarification before proceeding.

## Overview
ElevenTools is a modular, extensible platform for high-quality text-to-speech and local LLM workflows, focused on seamless integration with ElevenLabs (TTS) and Ollama (local LLMs). The project is designed for clarity, maintainability, and rapid iteration, with a strong emphasis on testability and developer onboarding.

---

## Tech Stack
- **Frontend:** Streamlit (Python)
- **Backend/Core Logic:** Python 3.10+
- **APIs:**
  - ElevenLabs (Text-to-Speech)
  - Ollama (Local LLM, e.g., llama3.2:3b)
- **Testing:** pytest, unittest.mock
- **Package & Environment Management:**
  - [`uv`](https://github.com/astral-sh/uv) (fast Python package and environment manager)
- **Environments:**
  - Local development (managed by uv)
  - No cloud dependencies; all LLMs run locally via Ollama

---

## Package & Environment Management

- All dependencies are listed in `requirements.txt` with explicit version pinning.
- Justification comments are included for each dependency.
- **Use `uv` for all dependency and environment management.**
- To set up the environment:
  ```sh
  uv venv .venv
  source .venv/bin/activate
  uv pip install -r requirements.txt
  ```
- For new packages:
  1. Review official documentation.
  2. Add to `requirements.txt` with a comment.
  3. Pin the version.
  4. Install with `uv pip install <package>`, then update `requirements.txt`.
- **Rationale:** `uv` is significantly faster than pip and venv, provides reproducible environments, and is recommended for all contributors for consistency and speed.

---

## Environments
- **Local Development:**
  - Python 3.12+ (managed by uv)
  - Ollama must be installed and running locally for LLM features
  - ElevenLabs API key required for TTS features
- **Environment Variables & Secrets:**
  - All API keys and secrets are managed via `st.secrets` (Streamlit secrets management)
  - Never hardcode secrets in code

---

## Project Structure
- `app.py` — Main Streamlit entry point
- `pages/` — Streamlit multipage app structure (Voice Design, Bulk Generation, Translation, etc.)
- `scripts/` — Core business logic and API integrations
- `tests/` — All tests (unit, integration, UI)
- `docs/` — Documentation (design.md, architecture.md, todo.md)

---

## Development Guidelines
- **Task Management:**
  - All work is tracked in `docs/todo.md` (see custom rules)
  - Never delete tasks; mark as complete with ✅
  - Break down complex tasks (>5/10) into subtasks
- **Design Alignment:**
  - All features must align with `docs/design.md`
  - Propose design changes before implementation
- **Code Quality:**
  - Write clear, well-documented code
  - Use type hints where possible
  - Follow PEP8 and project-specific linting rules
- **Testing:**
  - All new features must include tests
  - Mock all external API calls in tests
  - Cover both success and failure modes
  - Use fixtures for shared setup
- **Documentation:**
  - Update `README.md` and relevant docs for new features
  - Document all public functions/classes
  - Add usage examples for new features
- **Secrets Management:**
  - Use `st.secrets` for all API keys and sensitive config
  - Document secret requirements in `README.md`

---

## Best Practices
- **Modularity:**
  - Keep business logic separate from UI code
  - Use helper functions and modules for repeated logic
- **Error Handling:**
  - Always provide user-friendly error messages
  - Log errors for debugging
- **Performance:**
  - Cache API results where possible
  - Optimize for batch/bulk operations
- **Onboarding:**
  - Ensure onboarding flows (especially for Ollama) are beginner-friendly
  - Provide clear error/help messages for missing dependencies
- **Version Control:**
  - Use feature branches for development
  - Keep PRs focused and well-documented

---

## Getting Started (For New Developers)
1. Clone the repo and create a virtual environment with `uv venv .venv`
2. Activate the environment: `source .venv/bin/activate`
3. Install dependencies with `uv pip install -r requirements.txt`
4. Set up `st.secrets` with your ElevenLabs API key
5. Install and start Ollama locally (see README for instructions)
6. Run the app with `streamlit run app.py`
7. Run tests with `pytest`

---

## Additional Notes
- **No OpenAI/OpenRouter:** This release only supports Ollama (local) and ElevenLabs
- **No new features:** Focus is on polish, onboarding, and stability
- **Testing:** See `tests/` for examples and coverage; add UI onboarding tests as needed

---

## Version Control & Branching Model

- `main`: Production branch, always stable and deployable. All releases are tagged from here.
- `develop`: Ongoing development branch. All new features and bugfixes are merged here before going to main.
- `cloud`: Experimental or cloud-specific features branch, based on develop.

**Recent update:**
- `main` was updated to match `develop` (June 2024).
- `cloud` branch created from `develop` for cloud-specific work

---

For further details, see `docs/design.md` and `docs/todo.md`.
