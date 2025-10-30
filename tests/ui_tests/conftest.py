"""Shared fixtures for Playwright UI tests."""

import pytest
import subprocess
import time
from pathlib import Path


def _check_server_running(url: str) -> bool:
    """Check if Streamlit server is already running."""
    try:
        import requests

        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def streamlit_server():
    """Start Streamlit server for UI tests."""
    port = 8501
    host = "localhost"
    url = f"http://{host}:{port}"

    # Check if Streamlit is already running
    if _check_server_running(url):
        yield url
        return

    # Start Streamlit server
    app_path = Path(__file__).parent.parent.parent / "app.py"
    process = subprocess.Popen(
        [
            "uv",
            "run",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(port),
            "--server.headless",
            "true",
            "--server.enableCORS",
            "false",
            "--server.enableXsrfProtection",
            "false",
            "--browser.gatherUsageStats",
            "false",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    max_attempts = 30
    for _ in range(max_attempts):
        if _check_server_running(url):
            break
        time.sleep(1)
    else:
        process.terminate()
        pytest.fail("Streamlit server failed to start")

    yield url

    # Cleanup
    process.terminate()
    process.wait(timeout=10)


@pytest.fixture
def configured_page(page):  # pytest-playwright provides the page fixture
    """Configure page for UI tests with consistent viewport."""
    page.set_viewport_size({"width": 1280, "height": 720})
    yield page
