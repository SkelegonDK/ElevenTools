import os

import streamlit as st

from scripts.openrouter_functions import (
    DEFAULT_ENHANCEMENT_MODEL,
    DEFAULT_TRANSLATION_MODEL,
    fetch_openrouter_models,
    filter_free_models,
    get_openrouter_api_key,
    search_models_fuzzy,
)
from utils.error_handling import handle_error, validate_api_key

EXPECTED_KEYS = [
    ("ELEVENLABS_API_KEY", "ElevenLabs"),
    ("OPENROUTER_API_KEY", "OpenRouter"),
]

SECRETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml"
)


from typing import Optional


def render_model_selection(
    all_models: list,
    session_state_key: str,
    default_model_key: str,
    title: str,
    help_text: str = "",
) -> Optional[str]:
    """
    Render a reusable model selection UI component matching Translation page.

    Args:
        all_models: List of all available models from OpenRouter
        session_state_key: Key for storing search/filter state (e.g., "translation_model_search")
        default_model_key: Key for storing selected default model in session state
        title: Section title for the model selection
        help_text: Optional help text to display

    Returns:
        Selected model ID or None
    """
    st.subheader(title)
    if help_text:
        st.caption(help_text)

    # Initialize session state variables for this model selection
    search_key = f"{session_state_key}_search_query"
    free_filter_key = f"{session_state_key}_show_free_only"
    selected_key = f"{session_state_key}_selected"

    if search_key not in st.session_state:
        st.session_state[search_key] = ""
    if free_filter_key not in st.session_state:
        st.session_state[free_filter_key] = False

    # Free model filter
    show_free_only = st.checkbox(
        "Show only free models",
        value=st.session_state[free_filter_key],
        key=free_filter_key,
        help="Filter to show only models with zero cost",
    )

    # Fuzzy search input
    search_query = st.text_input(
        "Search models",
        value=st.session_state[search_key],
        key=search_key,
        placeholder="Type to search for models...",
        help="Search models by name (supports partial matches and typos)",
    )

    # Filter models based on search and free filter
    filtered_models = all_models.copy()

    # Apply free filter
    if show_free_only:
        filtered_models = filter_free_models(filtered_models, show_free_only=True)

    # Apply fuzzy search
    if search_query and search_query.strip():
        filtered_models = search_models_fuzzy(filtered_models, search_query.strip())

    # Create model options for selectbox
    selected_model_id = None
    if filtered_models:
        model_options = []
        model_dict = {}
        for model in filtered_models:
            model_id = model.get("id", "")
            model_name = model.get("name", model_id)
            display_name = (
                f"{model_name} ({model_id})" if model_name != model_id else model_id
            )
            model_options.append(display_name)
            model_dict[display_name] = model_id

        # Get current default model for this selection
        current_default = st.session_state.get(
            default_model_key,
            (
                DEFAULT_TRANSLATION_MODEL
                if "translation" in default_model_key
                else DEFAULT_ENHANCEMENT_MODEL
            ),
        )

        # Find index of current default if it exists in options
        default_index = 0
        if current_default in model_dict.values():
            for idx, display_name in enumerate(model_options):
                if model_dict[display_name] == current_default:
                    default_index = idx
                    break

        # Model selection dropdown
        selected_display = st.selectbox(
            "Select model",
            options=model_options,
            index=default_index if model_options else None,
            key=f"{session_state_key}_selectbox",
            help=f"Select a default model for {title.lower()}. Use search and filters above to narrow options.",
        )

        if selected_display:
            selected_model_id = model_dict.get(selected_display)

        # Show selected model info
        if selected_model_id:
            selected_model_data = next(
                (m for m in all_models if m.get("id") == selected_model_id),
                None,
            )
            if selected_model_data:
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Selected:** {selected_model_id}")
                with col2:
                    model_id = selected_model_data.get("id", "")
                    pricing = selected_model_data.get("pricing", {})
                    prompt_price = pricing.get("prompt", "N/A")
                    completion_price = pricing.get("completion", "N/A")

                    # Convert pricing to float for comparison (OpenRouter returns strings)
                    # Handle missing or non-numeric values as non-zero (not free)
                    try:
                        prompt_price_num = (
                            float(prompt_price)
                            if prompt_price != "N/A"
                            else float("inf")
                        )
                        completion_price_num = (
                            float(completion_price)
                            if completion_price != "N/A"
                            else float("inf")
                        )
                    except (ValueError, TypeError):
                        prompt_price_num = float("inf")
                        completion_price_num = float("inf")

                    is_free = model_id.endswith(":free") or (
                        prompt_price_num == 0 and completion_price_num == 0
                    )

                    if is_free:
                        st.success("🆓 Free model")
                    else:
                        st.caption(
                            f"Prompt: ${prompt_price}, Completion: ${completion_price}"
                        )
    else:
        if search_query or show_free_only:
            st.warning(
                "No models match your search criteria. Try adjusting your filters."
            )
        else:
            st.warning("No models available.")

    return selected_model_id


def main():
    st.set_page_config(page_title="Settings", page_icon="⚙️", layout="centered")
    st.title("Settings")
    st.info(
        """
        Configure your ElevenTools preferences including API keys and default model selections.\n\n
        value = st.session_state.get(env_key, st.secrets.get(env_key, None))
        They are never written to disk or shared between users.\n
        If you do not enter a key here, the app will use the key from Streamlit secrets (configured via Streamlit Cloud dashboard or local `.streamlit/secrets.toml`) if available.
        """
    )

    # Initialize default models in session state if not set
    if "default_translation_model" not in st.session_state:
        st.session_state["default_translation_model"] = DEFAULT_TRANSLATION_MODEL
    if "default_enhancement_model" not in st.session_state:
        st.session_state["default_enhancement_model"] = DEFAULT_ENHANCEMENT_MODEL

    # Section: Current API Keys
    st.header("API Key Management")
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
    st.subheader("Integration Status")
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
    st.subheader("Add or Update API Keys (Session Only)")
    st.markdown(
        """
        Enter your API keys below. These will be stored **only in your browser session** and are never saved to disk or shared.\n\n
        If you leave a field blank, the app will use the key from Streamlit secrets (configured via Streamlit Cloud dashboard or local `.streamlit/secrets.toml`) if available.\n\n
        To clear a key for this session, enter an empty value and click 'Save'.\n
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

    st.divider()

    # Section: Default Model Selection
    st.header("Default Model Configuration")
    st.markdown(
        """
        Configure default models for translation and script enhancement. These defaults will be used when no model is explicitly selected on individual pages.\n\n
        You can still override these defaults by selecting a different model on the Translation or main app pages.
        """
    )

    # Check if OpenRouter API key is available for model selection
    api_key = get_openrouter_api_key()
    if not api_key:
        st.warning(
            "⚠️ OpenRouter API key not found. Please configure your OpenRouter API key above to select default models."
        )
    else:
        # Fetch models with caching
        try:
            all_models = fetch_openrouter_models()
        except Exception as e:
            handle_error(e)
            st.warning("Could not fetch models. Please check your OpenRouter API key.")
            all_models = []

        if all_models:
            # Default Translation Model Selection
            selected_translation_model = render_model_selection(
                all_models=all_models,
                session_state_key="settings_translation",
                default_model_key="default_translation_model",
                title="Default Translation Model",
                help_text="This model will be used for translations when no model is selected on the Translation page.",
            )

            if selected_translation_model:
                st.session_state["default_translation_model"] = (
                    selected_translation_model
                )
                st.success(
                    f"✅ Default translation model set to: {selected_translation_model}"
                )

            st.divider()

            # Default Enhancement Model Selection
            selected_enhancement_model = render_model_selection(
                all_models=all_models,
                session_state_key="settings_enhancement",
                default_model_key="default_enhancement_model",
                title="Default Script Enhancement Model",
                help_text="This model will be used for script enhancement when no model is specified on the main app page.",
            )

            if selected_enhancement_model:
                st.session_state["default_enhancement_model"] = (
                    selected_enhancement_model
                )
                st.success(
                    f"✅ Default enhancement model set to: {selected_enhancement_model}"
                )

            # Manual refresh button
            if st.button("🔄 Refresh Model List"):
                fetch_openrouter_models.clear()
                st.rerun()
        else:
            st.warning(
                "No models available. Please check your OpenRouter API key and try refreshing."
            )

    st.divider()

    # Section: Troubleshooting & Docs
    st.header("Troubleshooting & Documentation")
    st.markdown(
        """
        - If you see a ❌ status, check that your key is present and valid in this session or in Streamlit secrets.
        - **Session keys** (entered here) take priority over Streamlit secrets.
        - **Default models** are stored in your browser session and will reset when you close the browser.
        - For local development, add keys to `.streamlit/secrets.toml`.
        - For Streamlit Cloud, configure secrets via the app settings dashboard.
        - For more help, see the [README.md](../README.md) or [Streamlit secrets documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management).
        """
    )


if __name__ == "__main__":
    main()
