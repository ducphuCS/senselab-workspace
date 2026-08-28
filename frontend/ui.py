"""Shared UI helpers for Compusense pages."""

import streamlit as st


def hide_default_header() -> None:
    """Hide Streamlit's default top bar and trim the main-area padding.

    Gives the app a minimal chrome. Note: this also removes the hamburger
    menu (sidebar toggle / settings) — remove this call to restore it.
    """
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] { display: none; }
        [data-testid="stMainBlockContainer"] { padding-top: 1.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
