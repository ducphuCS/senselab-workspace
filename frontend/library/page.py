"""Library workspace page — central hub for all pre-test registries."""

from __future__ import annotations

import streamlit as st
from frontend.library.test_methods.page import render as render_test_methods


def render() -> None:
    head_col, nav_col = st.columns([6, 1], vertical_alignment="center")
    with head_col:
        st.markdown("## 📚 Library")
    with nav_col:
        if st.button("← Dashboard", use_container_width=True):
            st.switch_page("dashboard/home.py")

    tab_methods, tab_panelists, tab_attributes, tab_panels = st.tabs(
        ["📋 Test Methods", "👥 Panelists", "🏷️ Attributes", "👥 Panels"]
    )

    with tab_methods:
        render_test_methods()

    with tab_panelists:
        st.subheader("👥 Panelists")
        st.info("Panelists registry is under development.")

    with tab_attributes:
        st.subheader("🏷️ Attributes & Attribute Sets")
        st.info("Attribute registry is under development.")

    with tab_panels:
        st.subheader("👥 Sensory Panels")
        st.info("Panels registry is under development.")


render()
