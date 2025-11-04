# UI Tests with Playwright

This directory contains end-to-end UI tests for the ElevenTools Streamlit application using Playwright.

## Setup

1. Install dependencies:
```bash
uv sync --extra dev
```

2. Install Playwright browsers:
```bash
uv run playwright install
```

## Running Tests

Run all UI tests:
```bash
uv run pytest tests/ui_tests/ -v
```

Run a specific test file:
```bash
uv run pytest tests/ui_tests/test_main_page.py -v
```

Run tests with headed browser (see what's happening):
```bash
uv run pytest tests/ui_tests/ --headed
```

Run tests with browser slow motion (helpful for debugging):
```bash
uv run pytest tests/ui_tests/ --headed --slowmo=1000
```

## Test Structure

- `conftest.py` - Shared fixtures (Streamlit server startup)
- `test_main_page.py` - Tests for main app.py page
- `test_bulk_generation_page.py` - Tests for Bulk Generation page
- `test_file_explorer_page.py` - Tests for File Explorer page
- `test_translation_page.py` - Tests for Translation page
- `test_settings_page.py` - Tests for Settings page

## Prerequisites

- Streamlit app must be able to start (API keys may be required in `.streamlit/secrets.toml`)
- Port 8501 must be available (or modify `conftest.py` to use different port)

## Configuration

The `conftest.py` fixture automatically starts a Streamlit server for testing. If you have Streamlit already running, the tests will use the existing instance.

## Notes

- Tests automatically start Streamlit in headless mode
- Each test gets a fresh page context
- Tests wait for network idle before assertions
- Some tests are conditional (checking for content that may or may not exist)

