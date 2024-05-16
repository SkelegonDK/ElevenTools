import streamlit as st
from functions import detect_phonetic_variables, detect_string_variables
from Elevenlabs import generate_audio
import random


ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
OPENAI_API = st.secrets["OPENAI_API_KEY"]

if "voice_id" not in st.session_state:
    st.session_state["voice_id"] = []

st.title("Pro Labs")
st.subheader("A professional interface for Elevenlabs")

selected_voice = st.selectbox("Select voice", st.session_state["voice_id"])
select_model = st.selectbox(
    "Select model",
    ["eleven_monolingual_v1", "eleven_multilingual_v2", "eleven_turbo_v2"],
)

script = st.text_area("Text to speech", height=100)

if script:
    detected_variables = detect_string_variables(script)
    detect_phonetic = detect_phonetic_variables(script)

    if detected_variables and len(detected_variables) > 0:
        st.info("Detected variables")
        variables_exp = st.expander("Text variables", expanded=True)
        with variables_exp:
            for variable in detected_variables:
                value = st.text_input(f"Edit: {variable}", key=variable)
                if value:
                    script = script.replace(f"{{{variable}}}", value)
            st.toast("Updated script", icon="🔄")
            updated_script = st.markdown(
                f"""
#### Updated script
{script}
"""
            )
    if detect_phonetic and len(detect_phonetic) > 0:
        st.info("Detected phonetic variables")
        phonetic_exp = st.expander("Phonetic variables", expanded=True)
        with phonetic_exp:
            for phonetic in detect_phonetic:
                value = st.text_input(f"Edit: {phonetic}", key=phonetic)
                if value:
                    script = script.replace(f"[[{phonetic}]]", value)
            st.toast("Updated script", icon="🔄")
            updated_script = st.markdown(
                f"""#### Updated phonetic spelling:
                {script}"""
            )


voice_settings = st.expander("Advanced voice settings", expanded=True)

with voice_settings:
    voice_similarity = st.slider("Voice similarity", 0.0, 1.0, 0.5)
    voice_stability = st.slider("Voice stability", 0.0, 1.0, 0.5)
    voice_style = st.slider("Voice style", 0.0, 1.0, 0.0)
    speaker_boost = st.checkbox("Use speaker boost")

random_seed = random.randint(100000, 999999)
# locked_seed = st.selectbox("Select seed", [random_seed, "Custom seed"])

generate_audio_btn = st.button("Generate Random Audio")

if generate_audio_btn:
    generate_audio(
        ELEVENLABS_API_KEY,
        voice_stability,
        select_model,
        voice_similarity,
        voice_style,
        speaker_boost,
        selected_voice,
        # Ensure this is the text to be spoken
        script,
        "output.mp3",
        seed=random_seed,
    )


####### Sidebar #######
sidebar = st.sidebar

with sidebar:
    add_voice_ID = sidebar.text_input("Add voice ID")
    add_voice_btn = sidebar.button("Add voice")

    add_seed = sidebar.text_input("Add seed")
    add_seed_btn = sidebar.button("Add seed", key="seed")

    settings = sidebar.expander("Settings", expanded=True)

    if add_voice_btn:
        st.session_state["voice_id"].append(add_voice_ID)
        st.write(st.session_state["voice_id"])
        st.toast("Press R the update the list", icon="♻️")
