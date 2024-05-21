from openai import OpenAI
import streamlit as st


def convert_word_to_phonetic(word: str, language: str):
    """
    Convert a word to its phonetic spelling in a given language using GPT-4.
    """

    # Construct the prompt
    prompt = f"""
    Convert the word "{word}" into the phonetic spelling appropriate for the "{language}" language
    Only respond with the phonetic spelling of the word, nothing else.
    """

    # Initialize the OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    with st.spinner("Loading response..."):
        try:
            # Make the API call to OpenAI
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert linguist and translator.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=15,
            )

            # Ensure there is a response

            if completion.choices[0]:
                # Access and return the content from the response
                return completion.choices[0].message.content
            else:
                st.toast("Phonetic conversion failed.")
                return None
        except Exception as e:

            st.error(f"An error occurred: {e}")
            return None
