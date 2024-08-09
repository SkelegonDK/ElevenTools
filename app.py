import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
pg = st.navigation(
    [
        st.Page("navigation/Home.py", title="Advanced Text-to-Speech"),
        st.Page("navigation/Bulk_Generation.py", title="Bulk Generation"),
    ]
)
pg.run()
