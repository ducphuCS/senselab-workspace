# Agent Guidelines — Compusense Sensory Lab Workspace

## 1. Project Overview & Domain Context

**Compusense** is a centralized workspace for the daily operations of a Sensory Lab supporting product development.

The system is organized into **4 core functional groups / bounded contexts**:

| Functional Group | Route Prefix | Frontend Location | Key Responsibilities & Entities |
|---|---|---|---|
| **Overview** | `/api/overview` | `frontend/dashboard/`, `frontend/overview/` | Workspace summary metrics, project progress, workloads, recent activity (`SummaryMetrics`, `ActivityLog`, `ProjectSummary`). |
| **Library** | `/api/library` | `frontend/library/` | Pre-test registries and configurations: Test Methods (Discrimination, Descriptive, Hedonic), Attributes, Attribute Sets, Panels, Panelists (`TestMethod`, `AttributeSet`, `Attribute`, `Panel`). |
| **Lab** | `/api/lab` | `frontend/lab/` | Live test execution: Projects, Experiments, Test Sessions, Samples, 3-digit blind coding, serving order randomization, in-app ballots (`Project`, `Experiment`, `TestSession`, `Sample`, `ServingPlan`). |
| **Analyze** | `/api/analyze` | `frontend/analyze/` | Statistical computations: ANOVA tables, correlation matrix, panel performance (discrimination, consensus, reproducibility), sensory trends (`AnovaResult`, `CorrelationMatrix`, `PanelPerformance`, `TrendResult`). |

> **Key Reference Documents:**
> - `docs/PROGRAM.md`: Functional scope and decisions (Decisions D1–D11). Always consult this before assuming requirements or design.
> - `backend/README.md`: Backend architecture specification and package boundary rules.

---

## 2. Environment & CLI Commands

Python dependencies and execution are managed with **`uv`**.

```bash
# Run both Backend (:8000) and Frontend (:8501)
uv run python main.py

# Run Backend API only (Swagger docs at http://127.0.0.1:8000/docs)
uv run python main.py --backend-only

# Run Streamlit Frontend only (UI at http://localhost:8501)
uv run python main.py --frontend-only

# Run test suite (architecture boundary tests and unit tests)
uv run python -m unittest discover tests

# Dependency management
uv add <package_name>
uv sync
```

---

## 3. Folder Permission Rules

- **No permission needed:** Implement freely inside `backend/`, `frontend/`, and `tests/`.
- **Permission required:** Anything outside those folders (`main.py`, `pyproject.toml`, `README.md`, `AGENTS.md`, `docs/`, `.gitignore`, `.python-version`, `uv.lock`, etc.) — always ask the user first.

---

## 4. Working Pace & Incremental Execution Rules

1. **One Small Step at a Time (Micro-Milestones):**
   - Never batch multiple components, entities, or services into a single response.
   - Break every task down into small, focused, single-concern steps.
2. **Check in After Each Step:**
   - Execute only one small piece of work per turn (e.g., a single schema, repository function, or endpoint).
   - Report back with a concise summary of exactly what was modified/created and wait for user review/confirmation before proceeding to the next step.
3. **Vertical Slices:**
   - Prefer implementing one feature/entity end-to-end in small incremental steps rather than scaffolding large horizontal layers across multiple domains.

---

## 5. Backend Architecture & Package Boundary Rules

The backend follows a **Modular Service Architecture (Microservice-Ready Monolith)** under `backend/services/{service_name}/`. Always adhere to the boundary rules defined in `backend/README.md`:

1. **No Cross-Domain Private Imports:**
   - A service's `models.py` (ORM models) and `repository.py` (DB queries) are **strictly private**.
   - Services must only interact with each other via public schemas (`schemas.py`) or client interfaces (`client.py`).
2. **References by Scalar IDs Only:**
   - Never define cross-service ORM foreign keys or relationships (e.g. no `relationship("PanelistORM")` inside Lab models).
   - Use scalar IDs (e.g. `panelist_id: str`).
3. **Exchange DTOs / Pydantic Schemas:**
   - Never pass active ORM entity instances or DB sessions across service boundaries; always serialize to Pydantic schemas.
4. **Shared Kernel (`backend/core/`) is Domain-Agnostic:**
   - `core/` only contains generic infrastructure tools (database session engine, base models, token utilities). No domain entities or business logic.
5. **Enforce Boundary Tests:**
   - Ensure changes pass architectural boundary tests in `tests/test_architecture_boundaries.py`.

---

## 6. Frontend Architecture & Guidelines

1. **Page-per-Folder Modularization:**
   - Each page lives in its own dedicated folder under `frontend/<page>/` (e.g. `frontend/dashboard/`, `frontend/library/`, `frontend/lab/`, `frontend/analyze/`).
   - Page dispatch and shared routing are handled in `frontend/app.py`.
2. **API Bridge Pattern:**
   - Frontend pages communicate with the backend exclusively via `main.py` bridge functions (`api_get()`, `api_post()`, `backend_healthy()`) or dedicated client adapters.
   - Never hardcode backend URLs or import backend ORM models directly in frontend pages.
3. **Streamlit Built-in Philosophy (Decision D8):**
   - Prefer built-in Streamlit widgets and components; avoid over-customized HTML/CSS widgets where standard components suffice.
4. **Hub-and-Spoke Navigation Pattern (No Sidebar):**
   - App routing uses `st.navigation([...], position="hidden")` without a persistent sidebar.
   - **Home Page (`frontend/dashboard/home.py`):** Acts as the central landing workspace displaying summary metrics, recent activity, and launcher cards for each functional group (`Library`, `Lab`, `Analyze`).
   - **Card Navigation:** Clicking `"Open <Group>"` (e.g. `"Open Library"`) on the Home page routes via `st.switch_page("<group>/page.py")` to that functional group's hub page.
   - **Compact Single-Row Header:**
     - Hub pages place the title and return button (`"← Dashboard"`) on the **same single row** using `st.columns([6, 1], vertical_alignment="center")` to maximize vertical space efficiency.
     - Content is organized into `st.tabs` directly below the single-row header.
   - **Flat URL Paths:** `st.Page(url_path=...)` must never contain nested slashes `/` (e.g. use `url_path="library"`, not `"library/home"`).

---

## 7. Git & Commit Discipline Rules

1. **State Commit Intent Before Committing:**
   - When the user says *"Approve to commit"*, always state the exact intention before running the commit:
     - Exact list of files to stage/commit.
     - Any files that will remain unstaged.
     - Proposed commit message.
2. **Short & Focused Commits:**
   - Prefer small, atomic, single-concern commits (e.g. docs-only, single schema, single router endpoint) over broad multi-component batches.
   - Never mix unrelated concerns (e.g., documentation vs. service implementation vs. configuration) in a single commit.

---

## 8. Living Document & Conflict Notification

1. **Evolving Guidelines:**
   - Guidelines, rules, and architectural patterns in this project are living agreements that evolve with project needs, not rigid or unchangeable dogmas.
2. **Proactive Conflict & Drift Notification:**
   - Whenever a requirement, architectural necessity, edge case, or practical implementation detail conflicts with or strains existing rules (in `AGENTS.md`, `docs/PROGRAM.md`, or backend specs), **proactively notify the user immediately**.
   - Outline the conflict, the reason, and the proposed resolution so we can align and update the guidelines together before drifting too far.
