#!/usr/bin/env python3
"""
Merit Badge Manager - Streamlit Web UI

Author: GitHub Copilot
Issue: #16
"""

import streamlit as st

st.set_page_config(
    page_title="Merit Badge Manager",
    page_icon="🏕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏕️ Merit Badge Manager")
st.markdown("---")

st.info("Select a page from the sidebar to get started.")
