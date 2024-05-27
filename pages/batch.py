import streamlit as st
import random

selected_voice = st.selectbox("Select voice", st.session_state["voice_id"])
select_model = st.selectbox(
    "Select model",
    ["eleven_monolingual_v1", "eleven_multilingual_v2", "eleven_turbo_v2"],
)

script = st.text_area(
    "Text to speech",
    height=100,
    help="""Use curly braces to add variables.
    `Example: {name} is a {job_title}.`
    Use double square brackets to add phonetic conversion.
    `Example: [[language:word]]`
    """,
)

voice_settings = st.expander("Advanced voice settings", expanded=True)

with voice_settings:
    voice_similarity = st.slider("Voice similarity", 0.0, 1.0, 0.5)
    voice_stability = st.slider("Voice stability", 0.0, 1.0, 0.5)
    voice_style = st.slider("Voice style", 0.0, 1.0, 0.0)
    speaker_boost = st.checkbox("Use speaker boost")

random_seed = random.randint(1000000000, 9999999999)

# locked_seed = st.selectbox("Select seed", [random_seed, "Custom seed"])


col1_generate, col2_generate, empty = st.columns(3, gap="small")

with col1_generate:

    generate_random_btn = col1_generate.button(
        "Generate with random seed", key="generate_audio_random"
    )

    if generate_random_btn:
        temp_filename = (
            f"VID_{selected_voice}_SEED_{random_seed}_UID_{uuid.uuid1()}.mp3"
        )
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
            temp_filename,
            seed=random_seed,
        )
# TODO: Implement fixed seed error

with col2_generate:
    generate_seed_btn = col2_generate.button(
        "Generate with fixed seed", key="generate_audio_seed"
    )
    if generate_seed_btn:
        if st.session_state["seed"] is "None":
            st.write(st.session_state["seed"])
            st.error("Please set a fixed seed")
        else:
            temp_filename = f"VID_{selected_voice}_SEED_{st.session_state['seed']}_UID_{uuid.uuid1()}.mp3"
            temp_seed = st.session_state["seed"]
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
                temp_filename,
                seed=temp_seed,
            )
