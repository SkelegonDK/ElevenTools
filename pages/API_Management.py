import streamlit as st
from utils.error_handling import validate_api_key, handle_error
import os

EXPECTED_KEYS = [
    ("ELEVENLABS_API_KEY", "ElevenLabs"),
    ("OPENROUTER_API_KEY", "OpenRouter"),
]

SECRETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml"
)


def main():
    st.set_page_config(page_title="API Management", page_icon="🔑", layout="centered")
    st.title("API Management")
    st.info(
        """
        This page shows the status of all API keys and secrets used by ElevenTools.\n\n"
        "API keys are stored in your browser session for privacy and per-user security.\n"
        "They are never written to disk or shared between users.\n"
        "If you do not enter a key here, the app will use the key from `.streamlit/secrets.toml` if available."
        """
    )

    # Section: Current API Keys
    st.header("Current API Keys & Status")
    key_status = []
    for env_key, service in EXPECTED_KEYS:
        # Prefer session state, fallback to st.secrets
        value = st.session_state.get(env_key) or st.secrets.get(env_key, None)
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
                "Source": (
                    "Session"
                    if env_key in st.session_state
                    else ("Secrets" if env_key in st.secrets else "Not set")
                ),
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
    st.header("Add or Update API Keys (Session Only)")
    st.markdown(
        """
        Enter your API keys below. These will be stored **only in your browser session** and are never saved to disk or shared.\n\n"
        "If you leave a field blank, the app will use the key from `.streamlit/secrets.toml` if available.\n\n"
        "To clear a key for this session, enter an empty value and click 'Save'.\n"
        """
    )

    with st.form("api_key_form"):
        eleven_key = st.text_input(
            "ElevenLabs API Key",
            value=st.session_state.get("ELEVENLABS_API_KEY", ""),
            type="password",
            help="Your ElevenLabs API key. Stored only in this session.",
        )
        openrouter_key = st.text_input(
            "OpenRouter API Key",
            value=st.session_state.get("OPENROUTER_API_KEY", ""),
            type="password",
            help="Your OpenRouter API key. Stored only in this session.",
        )
        submitted = st.form_submit_button("Save API Keys")
        if submitted:
            if eleven_key:
                st.session_state["ELEVENLABS_API_KEY"] = eleven_key
            elif "ELEVENLABS_API_KEY" in st.session_state:
                del st.session_state["ELEVENLABS_API_KEY"]
            if openrouter_key:
                st.session_state["OPENROUTER_API_KEY"] = openrouter_key
            elif "OPENROUTER_API_KEY" in st.session_state:
                del st.session_state["OPENROUTER_API_KEY"]
            st.success("API keys updated for this session.")

    st.caption(
        "Never share your API keys publicly. Keys entered here are only stored in your browser session and will be cleared when you close the browser or tab."
    )

    # Section: Troubleshooting & Docs
    st.header("Troubleshooting & Documentation")
    st.markdown(
        """
        - If you see a ❌ status, check that your key is present and valid in this session or in `.streamlit/secrets.toml`.
        - For more help, see the [README.md](../README.md) or [Streamlit secrets documentation](https://docs.streamlit.io/streamlit-community-cloud/develop-and-deploy/app-secrets).
        - For key rotation and environment support, see your team or deployment documentation.
        """
    )


if __name__ == "__main__":
    main()
