"""Dashboard — home page of Compusense.

Rendering of the landing page. Pages live one-per-folder under
``frontend/<page>/`` and are dispatched by the router in ``frontend/app.py``.
"""

from __future__ import annotations

import streamlit as st

from main import api_get, backend_healthy


def _load_summary() -> dict:
    """Fetch home data through the bridge; fall back to the local placeholder
    so the page still renders while the backend is down (dev convenience)."""
    if not backend_healthy():
        return {}
    return api_get("/api/overview")


def render() -> None:
    st.title("🧪 Compusense — Sensory Lab Workspace")

    if backend_healthy():
        data = _load_summary()
    else:
        from backend.app.data import SUMMARY  # dev-only fallback

        data = SUMMARY
        st.warning("Live data is currently unavailable — showing sample data.")

    metrics = data.get("metrics", {})
    cols = st.columns(4)
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label=label.replace("_", " ").title(), value=value)

    st.divider()

    st.subheader("Workspace areas")
    group_cols = st.columns(len(data.get("groups", [])))
    for col, group in zip(group_cols, data.get("groups", [])):
        with col:
            with st.container(border=True):
                st.markdown(f"**{group['name']}**")
                st.markdown(
                    f"<div style='min-height: 3.5rem; font-size: 0.875rem; opacity: 0.75; line-height: 1.4;'>{group['description']}</div>",
                    unsafe_allow_html=True,
                )
                if group["key"] == "library":
                    if st.button("Open Library", key="group_library", use_container_width=True):
                        st.switch_page("library/page.py")
                else:
                    st.button(
                        f"Open {group['name']}",
                        key=f"group_{group['key']}",
                        use_container_width=True,
                        on_click=lambda g=group: st.toast(
                            f"'{g['name']}' is not implemented yet."
                        ),
                    )

    st.divider()

    st.subheader("Recent activity")
    activity = data.get("recent_activity", [])
    if activity:
        st.dataframe(activity, width="stretch", hide_index=True)
    else:
        st.caption("No activity yet.")


render()
