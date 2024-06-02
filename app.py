import streamlit as st
from functions import detect_string_variables, detect_phonetic_conversion
from Openai_functions import convert_word_to_phonetic
from Elevenlabs_functions import generate_audio, get_voice_id, fetch_voices
import uuid
import random
from pprint import pprint

# TODO: Implement elevenlabs Library
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
OPENAI_API = st.secrets["OPENAI_API_KEY"]

if ELEVENLABS_API_KEY is None:
    ELEVENLABS_API_KEY = "sk-dummy"
    st.warning("Elevenlabs API key not found. Using dummy key")

if OPENAI_API is None:
    OPENAI_API = "sk-dummy"
    st.warning("OpenAI API key not found. Using dummy key")

if "voice_id" not in st.session_state:
    st.session_state["voice_id"] = []
    st.warning("Please add voice ID")
if "seed" not in st.session_state:
    st.session_state["seed"] = "None"
if "voice_library" not in st.session_state:
    st.session_state["voice_library"] = fetch_voices(ELEVENLABS_API_KEY)
if "generated_audio" not in st.session_state:
    st.session_state["generated_audio"] = []

# st.write(st.session_state["voice_library"])
voice_names = [voice["name"] for voice in st.session_state["voice_library"]]

selected_voice = st.selectbox("Select voice", voice_names)

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

if script:
    detected_variables = detect_string_variables(script)
    detect_phonetic = detect_phonetic_conversion(script)

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
                f"""#### Updated script:
                                         {script}"""
            )
    if detect_phonetic and len(detect_phonetic) > 0:
        st.info("Detected phonetic conversion")
        phonetic_exp = st.expander("Phonetic conversion", expanded=True)
        with phonetic_exp:
            for phonetic in detect_phonetic:
                print(phonetic)
                language = phonetic[0]
                word = phonetic[1]

                script = script.replace(
                    f"[[{language}:{word}]]",
                    convert_word_to_phonetic(
                        word=word, language=language, model=select_model
                    ),
                )
            st.toast("Updated script", icon="🔄")
            st.subheader("Updated script")
            updated_script = st.markdown(f"""{script}""")

voice_settings = st.expander("Advanced voice settings", expanded=True)

with voice_settings:
    voice_similarity = st.slider(
        "Voice similarity",
        0.0,
        1.0,
        0.5,
        help="""**Definition:** Voice similarity refers to how closely a synthetic voice matches a target voice. It’s about making the generated voice sound like a specific person.
        **Example:** If you’re trying to create a synthetic version of Morgan Freeman’s voice, voice similarity measures how much the generated voice sounds like Morgan Freeman.
                """,
    )
    voice_stability = st.slider(
        "Voice stability",
        0.0,
        1.0,
        0.5,
        help="""**Definition:** Voice stability refers to how consistent the synthetic voice sounds over time. It’s about maintaining the same voice characteristics without unintended variations.
        **Example:** If a synthetic voice starts with a deep, calm tone, voice stability ensures it doesn’t suddenly become high-pitched or erratic during a long speech.""",
    )
    voice_style = st.slider(
        "Voice style",
        0.0,
        1.0,
        0.0,
        help="""**Definition:** Style exaggeration refers to the enhancement or amplification of certain vocal characteristics to make the synthetic voice more expressive or distinctive. It involves intentionally modifying elements like pitch, tone, and cadence to create a more dramatic or emphasized vocal style.
        **Example:** If you want the synthetic voice to sound more theatrical or emotional, style exaggeration can make a calm sentence sound more excited or a neutral statement sound more authoritative.
""",
    )
    speaker_boost = st.checkbox("Use speaker boost")

random_seed = random.randint(1000000000, 9999999999)

# locked_seed = st.selectbox("Select seed", [random_seed, "Custom seed"])


col1_generate, col2_generate, empty = st.columns(3, gap="small")
voice_id = get_voice_id(st.session_state["voice_library"], selected_voice)
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
            voice_id,
            # Ensure this is the text to be spoken
            script,
            temp_filename,
            seed=random_seed,
        )
        st.session_state["generated_audio"].append(
            {
                "filename": temp_filename,
                "seed": random_seed,
                "voice": selected_voice,
                "model": select_model,
                "voice_similarity": voice_similarity,
                "voice_stability": voice_stability,
                "voice_style": voice_style,
                "speaker_boost": speaker_boost,
                "script": script,
            }
        )
# TODO: Implement fixed seed error


with col2_generate:
    generate_seed_btn = col2_generate.button(
        "Generate with fixed seed", key="generate_audio_seed"
    )
    st.caption(st.session_state["seed"])
    if generate_seed_btn:
        if st.session_state["seed"] == "None":
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
                voice_id,
                # Ensure this is the text to be spoken
                script,
                temp_filename,
                seed=temp_seed,
            )
            st.session_state["generated_audio"].append(
                {
                    "filename": temp_filename,
                    "seed": random_seed,
                    "voice": selected_voice,
                    "model": select_model,
                    "voice_similarity": voice_similarity,
                    "voice_stability": voice_stability,
                    "voice_style": voice_style,
                    "speaker_boost": speaker_boost,
                    "script": script,
                }
            )

Generated_audio = st.expander("Generated audio", expanded=True)
with Generated_audio:
    for audio in st.session_state["generated_audio"]:
        st.write(
            audio,
        )
        st.audio(audio["filename"], format="audio/mp3")

####### Sidebar #######
sidebar = st.sidebar

with sidebar:
    st.title("Pro Labs")
    st.write("A professional interface for Elevenlabs")

    fixed_seed = sidebar.text_input(
        "Fixed Seed", help="Set a fixed seed to improve reproducibility."
    )
    st.caption(
        """Setting a fixed seed will ensure that the audio generated is consistent across runs."
        For example when using variables in the script."""
    )
    st.session_state["seed"] = fixed_seed

    settings = sidebar.expander("Settings", expanded=True)
