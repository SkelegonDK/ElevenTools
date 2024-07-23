import streamlit as st
import pandas as pd
import os
from Elevenlabs_functions import bulk_generate_audio

st.set_page_config(page_title="Bulk Generation", page_icon="📚", layout="wide")

st.title("Bulk Generation")

st.write(
    """
Upload a CSV file with the following columns:
- 'text': The text to be converted to speech. Use {variable_name} for variables and \\n for new lines.
- 'filename' (optional): Custom filename for the generated audio.
- Any additional columns will be treated as variables to replace in the text.

Example CSV content:
```
text,filename,name,job
Hello {name}!\\nYou are a great {job}.,greeting_john,John,developer
Welcome {name}!\\nHow's your work as a {job}?,greeting_jane,Jane,designer
```

Note: The voice settings applied will be the same as set in the main page's 'Settings' section.
"""
)

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    st.write("CSV file uploaded successfully. Preview:")
    df = pd.read_csv(uploaded_file)
    st.write(df.head())

    # Create a button to trigger bulk generation
    if st.button("Generate Bulk Audio"):
        output_dir = "bulk_output"
        os.makedirs(output_dir, exist_ok=True)

        results_df = bulk_generate_audio(
            st.session_state["ELEVENLABS_API_KEY"],
            st.session_state["selected_model_id"],
            st.session_state["selected_voice_id"],
            uploaded_file,
            output_dir,
            st.session_state["voice_settings"],
        )

        if not results_df.empty:
            st.success("Bulk generation completed!")
            st.write("Generation Results:")
            st.write(results_df)

            # Add download buttons for each generated audio file
            for index, row in results_df.iterrows():
                if row["success"]:
                    with open(os.path.join(output_dir, row["filename"]), "rb") as file:
                        st.download_button(
                            label=f"Download {row['filename']}",
                            data=file,
                            file_name=row["filename"],
                            mime="audio/mpeg",
                        )
        else:
            st.error(
                "Bulk generation failed. Please check the logs for more information."
            )
else:
    st.info("Please upload a CSV file to begin bulk generation.")
