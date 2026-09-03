# Agent Guidelines

## Folder Permission Rules

- **No permission needed:** implement freely inside `backend/`, `frontend/`, and `tests/`.
- **Permission required:** anything outside those folders (`main.py`, `pyproject.toml`, `README.md`, `AGENTS.md`, `docs/`, `.gitignore`, `.python-version`, `uv.lock`, etc.) — always ask the user first.

---

## Working Pace & Incremental Execution Rules

1. **One Small Step at a Time (Micro-Milestones):**
   - Never batch multiple components, entities, or services into a single response.
   - Break every task down into small, focused, single-concern steps.
2. **Check in After Each Step:**
   - Execute only one small piece of work per turn (e.g., a single schema, repository function, or endpoint).
   - Report back with a concise summary of exactly what was modified/created and wait for user review/confirmation before proceeding to the next step.
3. **Vertical Slices:**
   - Prefer implementing one feature/entity end-to-end in small incremental steps rather than scaffolding large horizontal layers across multiple domains.

---

## Backend Architecture & Package Boundary Rules

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

## Git & Commit Discipline Rules

1. **State Commit Intent Before Committing:**
   - When the user says *"Approve to commit"*, always state the exact intention before running the commit:
     - Exact list of files to stage/commit.
     - Any files that will remain unstaged.
     - Proposed commit message.
2. **Short & Focused Commits:**
   - Prefer small, atomic, single-concern commits (e.g. docs-only, single schema, single router endpoint) over broad multi-component batches.
   - Never mix unrelated concerns (e.g., documentation vs. service implementation vs. configuration) in a single commit.


