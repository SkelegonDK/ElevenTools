# Contributing to ElevenTools

Thank you for your interest in contributing to ElevenTools! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ElevenTools.git
   cd ElevenTools
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev --all-groups
   ```

3. Install Playwright browsers (for UI tests):
   ```bash
   uv run playwright install
   ```

4. Run the application:
   ```bash
   uv run streamlit run app.py
   ```

## Development Workflow

### Branching Model

- **main**: Production branch, always stable and deployable
- **develop**: Ongoing development branch
- **feature/**: Feature branches for new functionality
- **fix/**: Bug fix branches
- **docs/**: Documentation updates

### Creating a Pull Request

1. Create a new branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines below

3. Write or update tests for your changes

4. Ensure all tests pass:
   ```bash
   uv run pytest
   ```

5. Run linting and type checking:
   ```bash
   uv run black .
   uv run ruff check .
   uv run mypy . --ignore-missing-imports
   ```

6. Commit your changes with clear, descriptive commit messages:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

7. Push to your fork and create a Pull Request to `develop`

## Code Style Guidelines

### General Principles

- Follow PEP 8 and Python best practices
- Use type hints for all function parameters and return values
- Write clear, well-documented code with docstrings
- Keep business logic separate from UI code
- Use meaningful variable and function names

### Code Formatting

We use **Black** for automatic code formatting:

```bash
uv run black .
```

### Linting

We use **Ruff** for linting:

```bash
uv run ruff check .
```

### Type Checking

We use **MyPy** for type checking:

```bash
uv run mypy . --ignore-missing-imports
```

### Import Organization

We use **isort** for import organization:

```bash
uv run isort .
```

### Code Structure

- **UI components**: Place in `pages/` directory (Streamlit multipage app structure)
- **Business logic**: Place in `scripts/` directory, organized by domain
- **Utilities**: Place in `utils/` directory for reusable helpers
- **Tests**: Mirror source structure in `tests/` directory

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of the function.

    Longer description explaining what the function does,
    any important details, and usage examples.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
    """
    pass
```

## Testing Requirements

### Test Organization

- Tests mirror source structure (`tests/test_api/`, `tests/test_web/`, etc.)
- Unit tests for core functions
- Integration tests for API interactions
- UI tests using Playwright

### Writing Tests

1. **Test Naming**: Use descriptive names: `test_<function_name>_<scenario>()`
2. **Test Structure**: Follow Arrange-Act-Assert pattern
3. **Test Isolation**: Each test should be independent
4. **Mocking**: Mock all external API calls (ElevenLabs, OpenRouter, Ollama)

### Running Tests

```bash
# Run core test suite (default)
uv run pytest

# Run all tests including extended
uv run pytest -m "core_suite or extended"

# Run specific test file
uv run pytest tests/test_api/test_elevenlabs_core.py

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run UI tests
uv run pytest tests/ui_tests/
```

### Test Coverage

- All new features must include corresponding tests
- Aim for comprehensive coverage of core functionality
- Test both success and failure modes
- Test edge cases and error handling

## Commit Message Conventions

We follow conventional commit message format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add bulk generation with CSV support

- Add CSV file upload functionality
- Implement variable replacement in bulk generation
- Add progress tracking for bulk operations
```

## Security Guidelines

### API Keys and Secrets

- **Never** commit API keys or secrets to the repository
- Use `st.secrets` for local development
- Use session-based storage for cloud deployment
- All secrets files are in `.gitignore`

### Input Validation

- Always validate user input before processing
- Use functions from `utils/security.py` for validation
- Check file sizes, row counts, and text lengths
- Sanitize all file paths before use

### Path Traversal Prevention

- Use `sanitize_path_component()` for user-provided filenames
- Use `validate_path_within_base()` for path validation
- Never use user input directly in file paths

## Pull Request Process

1. **Before Submitting**:
   - Ensure all tests pass
   - Run linting and type checking
   - Update documentation if needed
   - Add tests for new features

2. **PR Description**:
   - Clearly describe what the PR does
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

3. **Review Process**:
   - At least one maintainer must approve
   - Code must follow style guidelines
   - Tests must pass and coverage maintained

## Reporting Issues

When reporting issues, please include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant error messages or logs

## Questions?

If you have questions about contributing, please:

- Open an issue for discussion
- Check existing documentation in `docs/`
- Review the project structure in `openspec/project.md`

Thank you for contributing to ElevenTools!

