"""Compusense frontend entry — the router between pages.

Only shared app chrome (page config, header) and page dispatch live here;
each page's content lives in its own folder under ``frontend/<page>/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Make the root bridge importable no matter where streamlit is launched from.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from frontend.ui import hide_default_header  # noqa: E402

st.set_page_config(
    page_title="Compusense — Sensory Lab Workspace",
    page_icon="🧪",
    layout="wide",
)
hide_default_header()

dashboard = st.Page(
    "dashboard/home.py",
    title="Dashboard",
    url_path="dashboard",
    default=True,
)

library = st.Page(
    "library/page.py",
    title="Library",
    url_path="library",
)

st.navigation([dashboard, library], position="hidden").run()
