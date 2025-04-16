import streamlit as st
from utils.error_handling import validate_api_key, handle_error
import os

EXPECTED_KEYS = [
    ("ELEVENLABS_API_KEY", "ElevenLabs"),
]

SECRETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml"
)


def main():
    st.set_page_config(page_title="API Management", page_icon="🔑", layout="centered")
    st.title("API Management")
    st.info(
        """
        This page shows the status of all API keys and secrets used by ElevenTools. 
        All keys are securely managed via Streamlit's `st.secrets` and `.streamlit/secrets.toml`.
        """
    )

    # Section: Current API Keys
    st.header("Current API Keys & Status")
    key_status = []
    for env_key, service in EXPECTED_KEYS:
        value = st.secrets.get(env_key, None)
        try:
            validate_api_key(value, service)
            status = "✅ Valid"
        except Exception as e:
            status = f"❌ {str(e)}"
        key_status.append(
            {
                "Service": service,
                "Key Name": env_key,
                "Status": status,
            }
        )

    st.table(key_status)

    # Section: Integration Status
    st.header("Integration Status")
    enabled = [s for s in key_status if s["Status"].startswith("✅")]
    disabled = [s for s in key_status if not s["Status"].startswith("✅")]
    st.success(
        f"Enabled: {', '.join([s['Service'] for s in enabled])}"
        if enabled
        else "No integrations enabled."
    )
    st.warning(
        f"Disabled: {', '.join([s['Service'] for s in disabled])}"
        if disabled
        else "All integrations enabled."
    )

    # Section: Add/Update API Keys
    st.header("Add or Update API Keys")
    st.markdown(
        """
        1. Open the `.streamlit/secrets.toml` file in your project root.
        2. Add or update your API keys in the following format:
        ```toml
        ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
        ```
        3. Save the file and reload this page.
        """
    )
    st.caption(
        "Never share your API keys publicly. Rotate keys regularly for security."
    )

    # Section: Troubleshooting & Docs
    st.header("Troubleshooting & Documentation")
    st.markdown(
        """
        - If you see a ❌ status, check that your key is present and valid in `.streamlit/secrets.toml`.
        - For more help, see the [README.md](../README.md) or [Streamlit secrets documentation](https://docs.streamlit.io/streamlit-community-cloud/develop-and-deploy/app-secrets).
        - For key rotation and environment support, see your team or deployment documentation.
        """
    )
