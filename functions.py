import streamlit as st
import re
from openai import OpenAI


@st.experimental_fragment()
def detect_string_variables(text: str):
    """
    Detects string variables in a given text
    """

    return re.findall(r"\{([^}]+)\}", text)


@st.experimental_fragment()
def detect_phonetic_variables(text: str):
    """
    detect string variables in double square brackets.
    """
    return re.findall(r"\[\[([^]]+)\]\]", text)


# detect phonetic conversion string format is [[language:word]]
@st.experimental_fragment()
def detect_phonetic_conversion(script: str):
    """
    detect phonetic conversion string format is [[language:word]], and returns a lis of dictoinaries with language and word.
    example: [{
        "language": "english",
        "word": "hello"
    }]
    """
    return re.findall(r"\[\[([^:]+):([^]]+)\]\]", script)


@st.experimental_fragment()
def convert_word_to_phonetic(word: str, language: str):
    """
    Convert a word to its phonetic spelling in a given language using GPT-4.
    """

    prompt = f"""
    ## Task:
    **Convert the word {word} into the phonetic spelling appropriate for the {language} language.**

    ### Instructions:
    1. **Identify the Word**: Determine the word that needs to be converted.
    2. **Identify the Language**: Determine the target language for phonetic conversion.
    3. **Research Pronunciation**: Look up or recall the correct pronunciation of the word in the target language.
    4. **Phonetic Spelling**: Convert the pronunciation into phonetic spelling using the International Phonetic Alphabet (IPA) or another phonetic transcription method if specified.
    5. **Verify Accuracy**: Ensure the phonetic spelling accurately represents the pronunciation in the target language.

    ### Examples:

    1. **Input**: English, "Amazon"
    - **Identify the Word**: Amazon
    - **Identify the Language**: English
    - **Research Pronunciation**: In English, Amazon is pronounced /ˈæməzɒn/.
    - **Phonetic Spelling**: /ˈæməzɒn/
    - **Output**: /ˈæməzɒn/

    2. **Input**: Spanish, "Amazon"
    - **Identify the Word**: Amazon
    - **Identify the Language**: Spanish
    - **Research Pronunciation**: In Spanish, Amazon is pronounced /amaˈson/.
    - **Phonetic Spelling**: /amaˈson/
    - **Output**: /amaˈson/

    3. **Input**: French, "Amazon"
    - **Identify the Word**: Amazon
    - **Identify the Language**: French
    - **Research Pronunciation**: In French, Amazon is pronounced /amazɔ̃/.
    - **Phonetic Spelling**: /amazɔ̃/
    - **Output**: /amazɔ̃/

    ### Prompt:
    **Take the language given and convert this specific word to the language given in phonetic spelling. 
    Follow the detailed steps to ensure accurate conversion and verification.**
    ### Response:
    just the phonetic spelling of the word in the language given. Nothing else.
    """
    # TODO: Fix openai_loader

    openai_loader = st.spinner("Loading response...")
    client = OpenAI(st.secrets["OPENAI_API_KEY"])
    with openai_loader:

        try:

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert linguist and are helping a user convert a word into phonetic spelling in a specific language.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=15,
            )

            if response.choices:
                st.toast("Phonetic conversion completed.")
                return response.choices[0].message["content"].strip()
            else:
                st.toast("Phonetic conversion failed.")
                return None
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return None
