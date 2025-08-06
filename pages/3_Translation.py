import streamlit as st
from scripts.Translation_functions import translate_script
from scripts.openrouter_functions import get_openrouter_api_key

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
        translation = translate_script(text, language)
        st.write("Translation:")
        st.write(translation)
