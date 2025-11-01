import streamlit as st
from scripts.Translation_functions import translate_script
from scripts.openrouter_functions import (
    get_openrouter_api_key,
    fetch_openrouter_models,
    search_models_fuzzy,
    filter_free_models,
)
from utils.error_handling import handle_error

with open("custom_style.css", encoding="utf-8") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

st.title("Script Translation")

# Check if OpenRouter API key is available
api_key = get_openrouter_api_key()
if not api_key:
    st.error(
        "OpenRouter API key not found. Please set your OpenRouter API key in the API Management page."
    )
    st.stop()

# Initialize session state variables
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
if "model_search_query" not in st.session_state:
    st.session_state.model_search_query = ""
if "show_free_only" not in st.session_state:
    st.session_state.show_free_only = False

# Fetch models with caching
try:
    all_models = fetch_openrouter_models()
except Exception as e:
    handle_error(e)
    st.warning("Could not fetch models. Using default model.")
    all_models = []
    st.session_state.selected_model = None

# Model selection section
st.subheader("Model Selection")

# Free model filter
show_free_only = st.checkbox(
    "Show only free models",
    value=st.session_state.show_free_only,
    key="show_free_only",
    help="Filter to show only models with zero cost",
)

# Fuzzy search input
search_query = st.text_input(
    "Search models",
    value=st.session_state.model_search_query,
    key="model_search_query",
    placeholder="Type to search for models...",
    help="Search models by name (supports partial matches and typos)",
)

# Filter models based on search and free filter
filtered_models = all_models.copy()

# Apply free filter
if show_free_only:
    filtered_models = filter_free_models(filtered_models, show_free_only=True)

# Apply fuzzy search
if search_query:
    filtered_models = search_models_fuzzy(filtered_models, search_query)

# Create model options for selectbox
if filtered_models:
    model_options = []
    model_dict = {}
    for model in filtered_models:
        model_id = model.get("id", "")
        model_name = model.get("name", model_id)
        # Format: "name (id)" or just "id" if no name
        display_name = f"{model_name} ({model_id})" if model_name != model_id else model_id
        model_options.append(display_name)
        model_dict[display_name] = model_id
    
    # Model selection dropdown
    selected_display = st.selectbox(
        "Select model",
        options=model_options,
        index=0 if model_options else None,
        key="model_selectbox",
        help="Select a model for translation. Use search and filters above to narrow options.",
    )
    
    if selected_display:
        st.session_state.selected_model = model_dict.get(selected_display)
    
    # Show selected model info
    if st.session_state.selected_model:
        selected_model_data = next(
            (m for m in all_models if m.get("id") == st.session_state.selected_model),
            None,
        )
        if selected_model_data:
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Selected:** {st.session_state.selected_model}")
            with col2:
                pricing = selected_model_data.get("pricing", {})
                prompt_price = pricing.get("prompt", "N/A")
                completion_price = pricing.get("completion", "N/A")
                if prompt_price == 0 and completion_price == 0:
                    st.success("🆓 Free model")
                else:
                    st.caption(f"Prompt: ${prompt_price}, Completion: ${completion_price}")
else:
    if search_query or show_free_only:
        st.warning("No models match your search criteria. Try adjusting your filters.")
    else:
        st.warning("No models available.")
    st.session_state.selected_model = None

# Manual refresh button
if st.button("🔄 Refresh Model List"):
    fetch_openrouter_models.clear()
    st.rerun()

st.divider()

# Input text
text = st.text_area("Enter text to translate")

# Select language
language = st.selectbox(
    "Select target language",
    [
        "Spanish",
        "French",
        "German",
        "Italian",
        "Portuguese",
        "Dutch",
        "Chinese",
        "Japanese",
        "Korean",
        "Russian",
    ],
)

# Generate translation
if st.button("Translate") and text:
    with st.spinner("Translating..."):
        model_to_use = st.session_state.selected_model if st.session_state.selected_model else None
        translation = translate_script(text, language, model=model_to_use)
        st.write("Translation:")
        st.write(translation)
