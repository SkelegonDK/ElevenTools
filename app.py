import streamlit as st


ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
OPENAI_API = st.secrets["OPENAI_API_KEY"]

if "voice_id" not in st.session_state:
    st.session_state["voice_id"] = []

st.title("Eleven Tools")
st.subheader("A better interface for Elevenlabs")
st.text_area("Text to speech", height=100)


select_model = st.selectbox(
    "Select model", ["Multilingual v1", "Multilingual v2", "Turbo v2"]
)

st.selectbox("Select voice", st.session_state["voice_id"])

generate_audio = st.button("Generate")


####### Sidebar #######

sidebar = st.sidebar
add_voice_ID = sidebar.text_input("Add voice ID")
add_voice_btn = sidebar.button("Add voice", key="add_voice")

if add_voice_btn:
    st.session_state["voice_id"].append(add_voice_ID)
    st.write(st.session_state["voice_id"])

if st.secrets["ELEVENLABS_API_KEY"] is None or "YOUR_API":
    eleven_api_text = sidebar.text_input("Elevenlabs API key")
    eleven_api_btn = sidebar.button("Save", key="save_eleven_api_key")

    if eleven_api_btn:
        st.info("API key saved")

if st.secrets["OPENAI_API_KEY"] is None or "YOUR_API":
    openai_api_text = sidebar.text_input("OpenAI API key")
    openai_api_btn = sidebar.button("Save", key="save_open_api_key")

    if openai_api_btn:
        st.info("API key saved")
