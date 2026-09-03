"""Frontend Page: Library → Test Methods.

Implements the central sensory test methods repository, preset configurations,
and direct handoff into Lab execution.
"""

from __future__ import annotations

from typing import Any
import streamlit as st

from frontend.library.test_methods.adapter import TestMethodsAPI


def _category_icon(category: str) -> str:
    icons = {
        "discrimination": "🎯",
        "descriptive": "📊",
        "hedonic": "❤️",
    }
    return icons.get(category.lower(), "🧪")


def _status_badge(status: str) -> str:
    badges = {
        "active": "🟢 Active",
        "draft": "🟡 Draft",
        "archived": "⚪ Archived",
    }
    return badges.get(status.lower(), status.title())


def _render_create_method_dialog() -> None:
    @st.dialog("➕ Create New Test Method")
    def create_dialog() -> None:
        with st.form("create_method_form", clear_on_submit=False):
            name = st.text_input("Method Name *", placeholder="e.g. Triangle Difference Test")
            category = st.selectbox(
                "Category *",
                options=["discrimination", "descriptive", "hedonic"],
                format_func=lambda c: f"{_category_icon(c)} {c.title()}",
            )
            description = st.text_area(
                "Description",
                placeholder="High-level purpose and application of this sensory test method...",
            )

            st.markdown("##### Execution Procedure")
            procedure_raw = st.text_area(
                "Procedure Steps (one step per line)",
                placeholder="1. Prepare test triads with 3-digit blind codes\n2. Serve randomized order to panelists\n3. Record chosen odd sample",
                height=100,
            )

            st.markdown("##### Theoretical Assumptions")
            assumptions_raw = st.text_area(
                "Assumptions (one assumption per line)",
                placeholder="Guessing probability p0 = 1/3\nSamples are homogeneous\nIndependent panelist evaluations",
                height=100,
            )

            st.divider()
            st.markdown("##### Initial Preset (Optional)")
            create_preset = st.checkbox("Define an initial preset now", value=False)
            preset_name = ""
            default_panelists: int | None = None
            default_samples: int | None = None
            lighting = ""
            palate_cleanser = ""

            if create_preset:
                preset_name = st.text_input("Preset Name", placeholder="Preset name")
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    default_panelists = st.number_input("Recommended Panelists", min_value=1, value=None, step=1)
                with p_col2:
                    default_samples = st.number_input("Samples evaluated", min_value=1, value=None, step=1)
                lighting = st.text_input("Sensory Booth Lighting", placeholder="e.g. Red masking light")
                palate_cleanser = st.text_input("Palate Cleanser Protocol", placeholder="e.g. Filtered water")

            submitted = st.form_submit_button("Create Test Method", type="primary", use_container_width=True)

            if submitted:
                if not name.strip():
                    st.error("Please enter a method name.")
                    return

                procedure_list = [line.strip() for line in procedure_raw.splitlines() if line.strip()]
                assumptions_list = [line.strip() for line in assumptions_raw.splitlines() if line.strip()]

                initial_presets = []
                if create_preset and preset_name.strip():
                    initial_presets.append(
                        {
                            "name": preset_name.strip(),
                            "is_default": True,
                            "prerequisites": {
                                "input_requirements": {
                                    "default_panelist_count": default_panelists,
                                    "default_sample_count": default_samples,
                                    "presentation_format": None,
                                },
                                "instructional_conditions": {
                                    "lighting": lighting.strip() or None,
                                    "palate_cleanser": palate_cleanser.strip() or None,
                                },
                                "panelist_eligibility": {},
                            },
                            "output_schema": {},
                        }
                    )

                payload = {
                    "name": name.strip(),
                    "category": category,
                    "description": description.strip() or None,
                    "procedure": procedure_list,
                    "assumptions": assumptions_list,
                    "initial_presets": initial_presets,
                }

                try:
                    new_method = TestMethodsAPI.create_method(payload)
                    st.session_state["selected_method_id"] = new_method["id"]
                    st.success(f"Test Method '{name}' created successfully!")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to create method: {exc}")

    create_dialog()


def _render_add_preset_dialog(method_id: str, method_name: str) -> None:
    @st.dialog(f"➕ Add Preset to '{method_name}'")
    def add_preset_dialog() -> None:
        with st.form("add_preset_form", clear_on_submit=False):
            name = st.text_input("Preset Name *", placeholder="e.g. High-Power 60-Judge Similarity")
            desc = st.text_input("Context / Description", placeholder="e.g. Used for beta-risk power testing")
            is_default = st.checkbox("Set as Default Preset", value=False)

            st.markdown("##### 📥 Input Parameters (Form Prefills for Lab)")
            col1, col2 = st.columns(2)
            with col1:
                panelists = st.number_input("Recommended Panelists", min_value=1, value=None, step=1)
            with col2:
                samples = st.number_input("Default Sample Count", min_value=1, value=None, step=1)
            pres_format = st.text_input(
                "Presentation Scheme",
                placeholder="e.g. 3-digit blind code, balanced randomized block",
            )

            st.markdown("##### ⚙️ Instructional & Environmental Conditions")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                lighting = st.text_input("Sensory Lighting", placeholder="e.g. Red masking light")
                temp = st.text_input("Serving Temperature", placeholder="e.g. 20°C ± 2°C")
            with c_col2:
                cleanser = st.text_input("Palate Cleanser", placeholder="e.g. Filtered room-temp water")
                rest_sec = st.number_input("Forced Rest Interval (sec)", min_value=0, value=None, step=5)

            st.markdown("##### 👥 Panelist Eligibility")
            qual = st.text_input("Qualification Requirement", placeholder="e.g. Screened sensory acuity")
            restr = st.text_input("Pre-test Restrictions", placeholder="e.g. Fasting instructions")

            submitted = st.form_submit_button("Add Preset", type="primary", use_container_width=True)

            if submitted:
                if not name.strip():
                    st.error("Please provide a preset name.")
                    return

                payload = {
                    "name": name.strip(),
                    "description": desc.strip() or None,
                    "is_default": is_default,
                    "prerequisites": {
                        "input_requirements": {
                            "default_panelist_count": panelists,
                            "default_sample_count": samples,
                            "presentation_format": pres_format.strip() or None,
                        },
                        "instructional_conditions": {
                            "lighting": lighting.strip() or None,
                            "temperature": temp.strip() or None,
                            "palate_cleanser": cleanser.strip() or None,
                            "rest_interval_seconds": rest_sec,
                        },
                        "panelist_eligibility": {
                            "qualification_level": qual.strip() or None,
                            "pre_test_restrictions": restr.strip() or None,
                        },
                    },
                    "output_schema": {},
                }

                try:
                    TestMethodsAPI.add_preset(method_id, payload)
                    st.success(f"Preset '{name}' added successfully!")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to add preset: {exc}")

    add_preset_dialog()


def _render_duplicate_dialog(method: dict[str, Any]) -> None:
    @st.dialog(f"📋 Duplicate Method: {method['name']}")
    def duplicate_dialog() -> None:
        st.write(
            "This will create a new editable **Draft** copy containing all presets from the original method. "
            "The new method will track lineage back to this source."
        )
        new_name = st.text_input("New Method Name", value=f"{method['name']} (Copy)")
        if st.button("Confirm Duplicate", type="primary", use_container_width=True):
            try:
                dup = TestMethodsAPI.duplicate_method(method["id"], new_name=new_name.strip() or None)
                st.session_state["selected_method_id"] = dup["id"]
                st.success("Method duplicated successfully!")
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to duplicate: {exc}")

    duplicate_dialog()


def render() -> None:
    st.subheader("📋 Sensory Test Methods")
    st.caption("Central methodology repository, operational conditions, and preset protocols for sensory evaluations.")

    if not TestMethodsAPI.is_healthy():
        st.error("Backend microservice is offline. Please launch backend with `python main.py`.")
        return

    # Top Control Bar
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        search_query = st.text_input("🔍 Search test methods", placeholder="Search by method name or description...", label_visibility="collapsed")
    with top_col2:
        if st.button("➕ New Test Method", type="primary", use_container_width=True):
            st.session_state["show_create_dialog"] = True

    if st.session_state.get("show_create_dialog"):
        st.session_state["show_create_dialog"] = False
        _render_create_method_dialog()

    # Filter chips / selectors
    filter_col1, filter_col2, _ = st.columns([2, 2, 4])
    with filter_col1:
        category_filter = st.selectbox(
            "Category",
            options=["all", "discrimination", "descriptive", "hedonic"],
            format_func=lambda c: "All Categories" if c == "all" else f"{_category_icon(c)} {c.title()}",
        )
    with filter_col2:
        status_filter = st.selectbox(
            "Status",
            options=["all", "active", "draft", "archived"],
            format_func=lambda s: "All Statuses" if s == "all" else _status_badge(s),
        )

    # Fetch methods
    try:
        methods = TestMethodsAPI.list_methods(
            category=category_filter,
            status=status_filter,
            search=search_query.strip() or None,
        )
    except Exception as exc:
        st.error(f"Error fetching test methods: {exc}")
        return

    if not methods:
        st.info("No test methods found matching your filters. Click **'+ New Test Method'** to create your first method.")
        return

    # Master-Detail Layout
    left_col, right_col = st.columns([1, 2])

    # Keep track of selected method in session state
    if "selected_method_id" not in st.session_state or not any(m["id"] == st.session_state["selected_method_id"] for m in methods):
        st.session_state["selected_method_id"] = methods[0]["id"]

    with left_col:
        st.markdown(f"**Methods Catalog** ({len(methods)})")
        for m in methods:
            is_selected = m["id"] == st.session_state["selected_method_id"]
            card_border = "2px solid #2563EB" if is_selected else "1px solid #E5E7EB"
            with st.container(border=True):
                m_top1, m_top2 = st.columns([3, 2])
                with m_top1:
                    st.markdown(f"**{_category_icon(m['category'])} {m['name']}**")
                with m_top2:
                    st.caption(_status_badge(m["status"]))

                st.caption(f"{len(m['presets'])} Presets • Used in {m['total_usage_count']} tests")
                if st.button("Select Method", key=f"sel_{m['id']}", use_container_width=True, type="secondary" if not is_selected else "primary"):
                    st.session_state["selected_method_id"] = m["id"]
                    st.rerun()

    # Detail Pane
    with right_col:
        selected_id = st.session_state["selected_method_id"]
        try:
            method = TestMethodsAPI.get_method(selected_id)
        except Exception as exc:
            st.error(f"Failed to load method details: {exc}")
            return

        with st.container(border=True):
            # Header
            head_col1, head_col2 = st.columns([3, 1])
            with head_col1:
                st.subheader(f"{_category_icon(method['category'])} {method['name']}")
                st.markdown(f"**Classification:** `{method['category'].title()}` &nbsp;|&nbsp; **Status:** {_status_badge(method['status'])}")
                if method.get("derived_from_id"):
                    st.caption(f"🔗 *Duplicated from method ID: `{method['derived_from_id'][:8]}...`*")
            with head_col2:
                st.metric("Total Lab Uses", method["total_usage_count"])

            if method.get("description"):
                st.markdown(f"*{method['description']}*")

            # Action Bar
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
            with btn_col1:
                if st.button("➕ Add Preset", key=f"add_p_{method['id']}", use_container_width=True):
                    st.session_state["show_add_preset_dialog"] = True
            with btn_col2:
                if st.button("📋 Duplicate", key=f"dup_{method['id']}", use_container_width=True):
                    st.session_state["show_dup_dialog"] = True
            with btn_col3:
                if method["status"] != "archived":
                    if st.button("📦 Archive", key=f"arch_{method['id']}", use_container_width=True):
                        TestMethodsAPI.archive_method(method["id"])
                        st.success(f"Method '{method['name']}' archived.")
                        st.rerun()
            with btn_col4:
                if method["total_usage_count"] == 0:
                    if st.button("🗑️ Delete Draft", key=f"del_{method['id']}", use_container_width=True):
                        TestMethodsAPI.delete_method(method["id"])
                        st.warning(f"Method '{method['name']}' deleted.")
                        st.session_state.pop("selected_method_id", None)
                        st.rerun()

            if st.session_state.get("show_add_preset_dialog"):
                st.session_state["show_add_preset_dialog"] = False
                _render_add_preset_dialog(method["id"], method["name"])

            if st.session_state.get("show_dup_dialog"):
                st.session_state["show_dup_dialog"] = False
                _render_duplicate_dialog(method)

            st.divider()

            # Methodology Details
            detail_tab1, detail_tab2 = st.tabs(["Execution Procedure", "Theoretical Assumptions"])
            with detail_tab1:
                if method.get("procedure"):
                    for idx, step in enumerate(method["procedure"], 1):
                        st.markdown(f"**Step {idx}:** {step}")
                else:
                    st.caption("No procedure steps registered.")

            with detail_tab2:
                if method.get("assumptions"):
                    for item in method["assumptions"]:
                        st.markdown(f"• {item}")
                else:
                    st.caption("No theoretical assumptions registered.")

            st.divider()

            # Presets Section
            st.markdown(f"### Presets & Protocols ({len(method['presets'])})")
            if not method["presets"]:
                st.warning("⚠️ No presets configured for this method yet. Click **'+ Add Preset'** to configure runnable protocols for Lab testing.")
            else:
                preset_tabs = st.tabs([f"{'⭐ ' if p['is_default'] else ''}{p['name']}" for p in method["presets"]])
                for tab, preset in zip(preset_tabs, method["presets"]):
                    with tab:
                        p_top1, p_top2 = st.columns([3, 1])
                        with p_top1:
                            st.markdown(f"**{preset['name']}** {' *(Default)*' if preset['is_default'] else ''}")
                            if preset.get("description"):
                                st.caption(preset["description"])
                        with p_top2:
                            if preset["usage_count"] > 0:
                                st.badge("Locked (In Use)", color="gray")
                            else:
                                st.badge("Draft", color="yellow")

                        prereqs = preset.get("prerequisites", {})
                        in_reqs = prereqs.get("input_requirements", {})
                        inst_cond = prereqs.get("instructional_conditions", {})
                        elig = prereqs.get("panelist_eligibility", {})

                        st.markdown("##### 📥 Input Parameters (Form Prefills for Lab)")
                        ip_col1, ip_col2, ip_col3 = st.columns(3)
                        ip_col1.metric("Recommended Panelists", in_reqs.get("default_panelist_count") or "N/A")
                        ip_col2.metric("Evaluated Samples", in_reqs.get("default_sample_count") or "N/A")
                        ip_col3.markdown(f"**Presentation Scheme:**\n{in_reqs.get('presentation_format') or 'Standard'}")

                        st.markdown("##### ⚙️ Instructional Conditions (Technician Checklist)")
                        st.markdown(f"- **Sensory Lighting:** {inst_cond.get('lighting') or 'Standard White'}")
                        st.markdown(f"- **Temperature:** {inst_cond.get('temperature') or 'Room Temperature (20°C ± 2°C)'}")
                        st.markdown(f"- **Palate Cleanser:** {inst_cond.get('palate_cleanser') or 'None'}")
                        st.markdown(f"- **Rest Interval:** {inst_cond.get('rest_interval_seconds') or 0} seconds between samples")

                        st.markdown("##### 👥 Panelist Eligibility")
                        st.markdown(f"- **Qualification:** {elig.get('qualification_level') or 'General / Any'}")
                        st.markdown(f"- **Restrictions:** {elig.get('pre_test_restrictions') or 'Standard protocol'}")

                        # Preset Actions
                        st.markdown("---")
                        p_act1, p_act2, _ = st.columns([1, 1, 2])
                        with p_act1:
                            if preset["status"] != "archived":
                                if st.button("📦 Archive Preset", key=f"arch_p_{preset['id']}"):
                                    TestMethodsAPI.archive_preset(preset["id"])
                                    st.success(f"Preset '{preset['name']}' archived.")
                                    st.rerun()
                        with p_act2:
                            if preset["usage_count"] == 0:
                                if st.button("🗑️ Delete Preset", key=f"del_p_{preset['id']}"):
                                    TestMethodsAPI.delete_preset(preset["id"])
                                    st.warning(f"Preset '{preset['name']}' deleted.")
                                    st.rerun()


if __name__ == "__main__":
    render()
