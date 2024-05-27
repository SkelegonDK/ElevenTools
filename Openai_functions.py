from openai import OpenAI
import streamlit as st


def convert_word_to_phonetic(word: str, language: str, model: str):
    """
    Convert a word to its phonetic spelling in a given language using GPT-4.
    """
    multilingual_v2_prompt = f"""
    You speak perfect {language}.
    Your goal is to pronounce this word correctly and help me not sound like a tourist. 
    When I type something in English, you will translate and also give me the phonetic pronunciation.
    Only respond with the phonetic pronunciation of the word, nothing else.
    """
    # Construct the prompt
    model_1_prompt = f"""
    You speak perfect {language}.
    Convert the word {word} into the phonetic spelling appropriate for the {language} language
    Only respond with the phonetic spelling of the word, nothing else.
    """

    # Initialize the OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if model == "eleven_monolingual_v1":
        prompt = model_1_prompt
    else:
        prompt = multilingual_v2_prompt

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
