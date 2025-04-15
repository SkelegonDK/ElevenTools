import streamlit as st
from scripts.Translation_functions import translate_script

with open("custom_style.css", encoding="utf-8") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

st.title("Script Translation")

# Input text
text = st.text_area("Enter text to translate")

# Select language
language = st.selectbox(
    "Select target language",
    ["Spanish", "French", "German", "Italian", "Portuguese", "Dutch"],
)

# Generate translation
if st.button("Translate") and text:
    translation = translate_script(text, language)
    st.write("Translation:")
    st.write(translation)
