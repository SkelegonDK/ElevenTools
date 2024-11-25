import streamlit as st
from Elevenlabs_functions import (
    fetch_voices,
    generate_audio,
    generate_voice_previews,
    create_voice_from_preview,
)
from ollama_functions import get_ollama_response

with open("custom_style.css", encoding="utf-8") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


def enhance_prompt(prompt):
    """Enhance the voice description prompt using Ollama."""
    system_message = f"""You are an expert in voice design and description. 
    Enhance the given voice description to be more detailed and professional, 
    focusing on voice characteristics, tone, emotion, and technical aspects.
    
    Please enhance this voice description: {prompt}"""

    enhanced = get_ollama_response(system_message)
    return enhanced


def get_prompt_suggestions():
    """Return a list of predefined voice prompt suggestions."""
    return [
        "A warm and friendly female voice with a slight British accent",
        "A deep, authoritative male voice suitable for documentaries",
        "A young, energetic voice with a modern American accent",
        "A soothing, calming voice with perfect pronunciation",
        "A professional and clear voice with natural intonation",
    ]


def copy_to_clipboard(text):
    """Create a button that copies text to clipboard using JavaScript."""
    js_code = f"""
        <script>
        function copyToClipboard() {{
            navigator.clipboard.writeText('{text}');
        }}
        </script>
        <button onclick="copyToClipboard()">📋 Copy ID</button>
    """
    st.components.v1.html(js_code, height=30)


# Initialize session state
if "ELEVENLABS_API_KEY" not in st.session_state:
    st.session_state["ELEVENLABS_API_KEY"] = st.secrets["ELEVENLABS_API_KEY"]
if "voice_prompt" not in st.session_state:
    st.session_state.voice_prompt = ""
if "generated_previews" not in st.session_state:
    st.session_state.generated_previews = None
if "played_ids" not in st.session_state:
    st.session_state.played_ids = []

st.title("Voice Design Studio")

# Voice prompt input section
col1, col2 = st.columns([2, 1])
with col1:
    st.session_state.voice_prompt = st.text_area(
        "Enter voice description",
        value=st.session_state.voice_prompt,
        height=100,
        help="Describe the voice you want to create. Be specific about characteristics like gender, age, accent, tone, and emotion.",
    )

    col3, col4 = st.columns(2)
    with col3:
        if st.button("Enhance Description"):
            with st.spinner("Enhancing description..."):
                enhanced_prompt = enhance_prompt(st.session_state.voice_prompt)
                st.session_state.voice_prompt = enhanced_prompt
                st.rerun()

    with col4:
        if st.button("Generate Voice Previews"):
            with st.spinner("Generating voice previews..."):
                previews = generate_voice_previews(
                    st.session_state["ELEVENLABS_API_KEY"],
                    st.session_state.voice_prompt,
                )
                if previews:
                    st.session_state.generated_previews = previews
                    st.rerun()

with col2:
    st.subheader("Suggestions")
    suggestions = get_prompt_suggestions()
    for suggestion in suggestions:
        if st.button(suggestion[:40] + "..."):
            st.session_state.voice_prompt = suggestion
            st.rerun()

# Voice preview section
if st.session_state.generated_previews:
    st.subheader("Generated Voice Previews")
    st.info(
        "Listen to the previews and select your favorite by creating a voice from it."
    )

    # Create voice form
    with st.form("create_voice_form"):
        voice_name = st.text_input(
            "Voice Name",
            placeholder="Enter a name for your voice",
            help="This name will be used to identify your voice in the system",
        )
        create_voice = st.form_submit_button("Create Voice")

        if create_voice and voice_name:
            with st.spinner("Creating voice..."):
                result = create_voice_from_preview(
                    st.session_state["ELEVENLABS_API_KEY"],
                    voice_name,
                    st.session_state.voice_prompt,
                    st.session_state.generated_previews["generated_voice_id"],
                    st.session_state.played_ids,
                )
                if result:
                    st.success(f"Voice '{voice_name}' created successfully!")
                    st.session_state.generated_previews = None
                    st.session_state.played_ids = []
                    st.rerun()

    # Display previews
    cols = st.columns(3)
    for idx, preview in enumerate(st.session_state.generated_previews["audio"]):
        with cols[idx % 3]:
            st.write(f"**Preview {idx + 1}**")
            st.audio(preview["path"])

            # Add to played IDs when audio is played
            if preview["id"] not in st.session_state.played_ids:
                st.session_state.played_ids.append(preview["id"])

# Available voices section
st.divider()
st.subheader("Available Voices")

# Get available voices
if "voices" not in st.session_state:
    st.session_state["voices"] = fetch_voices(st.session_state["ELEVENLABS_API_KEY"])

# Create columns for voice previews
cols = st.columns(3)
for idx, (voice_id, voice_name) in enumerate(
    st.session_state["voices"][:6]
):  # Show first 6 voices
    with cols[idx % 3]:
        st.write(f"**{voice_name}**")
        st.code(voice_id, language=None)

        # Copy button using JavaScript
        copy_to_clipboard(voice_id)

        # Generate preview button
        if st.button("🔊 Preview", key=f"preview_{voice_id}"):
            if st.session_state.voice_prompt:
                success, _ = generate_audio(
                    st.session_state["ELEVENLABS_API_KEY"],
                    stability=0.5,
                    model_id="eleven_multilingual_v2",
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                    voice_id=voice_id,
                    text_to_speak=st.session_state.voice_prompt,
                    output_path=f"preview_{voice_id}.mp3",
                )
                if success:
                    st.audio(f"preview_{voice_id}.mp3")
            else:
                st.warning("Please enter a voice description first.")
