"""Shared UI helpers for Compusense pages."""

import streamlit as st


def hide_default_header() -> None:
    """Hide Streamlit's default top bar and trim the main-area padding.

    Gives the app a minimal chrome and eliminates excess top white space.
    """
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] { display: none; }
        [data-testid="stMainBlockContainer"] { padding-top: 1rem; padding-bottom: 1.5rem; }
        .block-container { padding-top: 1rem; }
        h1, h2, h3 { margin-top: 0rem; margin-bottom: 0.25rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
