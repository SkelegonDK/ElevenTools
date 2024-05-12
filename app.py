import streamlit as st
from functions import detect_string_variables

ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
OPENAI_API = st.secrets["OPENAI_API_KEY"]

if "voice_id" not in st.session_state:
    st.session_state["voice_id"] = []

st.title("Elevenlabs Tools")
st.subheader("A better interface for Elevenlabs")

st.selectbox("Select voice", st.session_state["voice_id"])
select_model = st.selectbox(
    "Select model", ["Multilingual v1", "Multilingual v2", "Turbo v2"]
)

script = st.text_area("Text to speech", height=100)

if script:
    detected_variables = detect_string_variables(script)

    if detected_variables is not None:
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


voice_settings = st.expander("Advanced voice settings", expanded=True)

with voice_settings:
    voice_similarity = st.slider("Voice similarity", 0.0, 1.0, 0.5)
    voice_stability = st.slider("Voice stability", 0.0, 1.0, 0.5)
    voice_style = st.slider("Voice style", 0.0, 1.0, 0.0)


generate_audio = st.button("Generate")


####### Sidebar #######
sidebar = st.sidebar

with sidebar:
    add_voice_ID = sidebar.text_input("Add voice ID")
    add_voice_btn = sidebar.button("Add voice")

    settings = sidebar.expander("Settings", expanded=True)

    if add_voice_btn:
        st.session_state["voice_id"].append(add_voice_ID)
        st.write(st.session_state["voice_id"])
        st.toast("Press R the update the list", icon="♻️")

    if st.secrets["ELEVENLABS_API_KEY"] is None or "YOUR_API":
        eleven_api_text = settings.text_input("Elevenlabs API key")
        eleven_api_btn = settings.button("Save", key="save_eleven_api_key")

        if eleven_api_btn:
            st.toast("API key saved", icon="💾")

    if st.secrets["OPENAI_API_KEY"] is None or "YOUR_API":
        openai_api_text = settings.text_input("OpenAI API key")
        openai_api_btn = settings.button("Save", key="save_open_api_key")

        if openai_api_btn:
            st.toast("API key saved", icon="💾")
