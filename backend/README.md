# Backend Architecture Specification

This document defines the backend architecture for the **Compusense Sensory Lab Workspace**, implementing a **Modular Service Architecture (Microservice-Ready Monolith)** aligned with the 4 functional groups.

---

## 1. Architecture Overview

The backend is structured into domain services corresponding to the **4 functional groups** coordinated through an API Gateway / Application Hub:

```
                              ┌─────────────────────────────┐
                              │     Frontend (Streamlit)    │
                              └──────────────┬──────────────┘
                                             │ HTTP / REST
                                             ▼
                              ┌─────────────────────────────┐
                              │     API Gateway / Hub       │
                              │     (FastAPI on :8000)      │
                              └──────┬─────┬─────┬─────┬────┘
                                     │     │     │     │
            ┌────────────────────────┘     │     │     └────────────────────────┐
            ▼                              ▼     ▼                              ▼
 ┌─────────────────────┐       ┌───────────────┐ ┌───────────────────┐ ┌─────────────────────┐
 │  Overview Service   │       │Library Service│ │    Lab Service    │ │   Analyze Service   │
 │    /api/overview    │       │/api/v1/library│ │    /api/v1/lab    │ │  /api/v1/analyze    │
 ├─────────────────────┤       ├───────────────┤ ├───────────────────┤ ├─────────────────────┤
 │ • Workspace summary │       │ • Test Methods│ │ • Experiments     │ │ • ANOVA tables      │
 │ • Project overview  │       │ • Attribute   │ │ • Test sessions   │ │ • Correlation matrix│
 │ • Workloads metrics │       │   Sets        │ │ • Blind codes     │ │ • Panel performance │
 │ • Recent activity   │       │ • Attributes  │ │ • Serving order   │ │ • Sensory trends    │
 │                     │       │ • Panels      │ │   randomization   │ │                     │
 └─────────────────────┘       └───────────────┘ └───────────────────┘ └─────────────────────┘
```

---

## 2. Bounded Context Services (4 Functional Groups)

| Functional Group | Route Prefix | Primary Responsibilities | Domain Entities |
|---|---|---|---|
| **Overview** | `/api/overview` | Workspace metrics, experiment progress, workload tracking, recent activity | `SummaryMetrics`, `ActivityLog`, `ProjectSummary` |
| **Library** | `/api/v1/library` | Pre-test configurations and registries | `TestMethod`, `AttributeSet`, `Attribute`, `Panel` |
| **Lab** | `/api/v1/lab` | Live experiment lifecycle, test execution, 3-digit blind coding, sample serving order | `Project`, `Experiment`, `TestSession`, `Sample`, `ServingPlan` |
| **Analyze** | `/api/v1/analyze` | Statistical computations and results | `AnovaResult`, `CorrelationMatrix`, `PanelPerformance`, `TrendResult` |

---

## 3. Directory Layout

```
backend/
├── app/
│   ├── main.py                  # API Gateway / Application Hub (mounts service routers)
│   ├── data.py                  # In-memory placeholder data store
│   └── routers/
│       └── overview.py          # Endpoint: /api/overview
├── core/                        # Shared infrastructure mixins & base classes
│   └── base_model.py            # Base declarative models / common schema mixins
├── services/
│   ├── library/                 # === Library Service ===
│   │   ├── __init__.py
│   │   ├── router.py            # Endpoints: /api/v1/library/*
│   │   ├── models.py            # (Private) ORM database models
│   │   ├── schemas.py           # (Public) Pydantic schemas / DTOs
│   │   ├── repository.py        # (Private) Database access layer
│   │   └── client.py            # (Public) In-process / HTTP client adapter
│   │
│   ├── lab/                     # === Lab Service ===
│   │   ├── __init__.py
│   │   ├── router.py            # Endpoints: /api/v1/lab/*
│   │   ├── models.py            # (Private) ORM database models
│   │   ├── schemas.py           # (Public) Pydantic schemas / DTOs
│   │   ├── repository.py        # (Private) Database access layer
│   │   └── engine/              # Core algorithms
│   │       ├── randomization.py # Serving order randomization
│   │       └── blind_coding.py  # 3-digit blind code generation
│   │
│   └── analyze/                 # === Analyze Service ===
│       ├── __init__.py
│       ├── router.py            # Endpoints: /api/v1/analyze/*
│       ├── schemas.py           # (Public) Pydantic schemas / DTOs
│       └── stats/               # Numerical & statistical computation
│           ├── anova.py         # One-way ANOVA computation
│           ├── correlation.py   # Correlation matrices
│           ├── performance.py   # Panel discrimination & consensus
│           └── trends.py        # Longitudinal trend analysis
└── README.md
```

---

## 4. Package Boundary Discipline Rules

To ensure true modularity and allow any service to be extracted into a standalone deployable process at any time without refactoring, all backend code must strictly adhere to the following rules:

### Rule 1: Never Import Private Internals Across Services
Each service’s `models.py` (ORM definitions) and `repository.py` (SQL query layer) are **strictly private** to that service package.

```python
# ❌ VIOLATION: Lab directly importing Library's internal repository or ORM models
from backend.services.library.repository import PanelRepository
from backend.services.library.models import PanelORM

# ✅ CORRECT: Lab interacts only with public schemas or public client interfaces
from backend.services.library.schemas import PanelRead
from backend.services.library.client import LibraryClient
```

### Rule 2: References by Identifier Only (No Cross-Domain ORM Relationships)
Never define ORM foreign keys or table joins (`relationship()`) across domain service boundaries. Use scalar IDs (`str` or `int`).

### Rule 3: Exchange DTOs (Pydantic Schemas), Never Raw ORM Instances
Services must communicate strictly using serialized Data Transfer Objects (Pydantic schemas). Never pass active database sessions or un-serialized ORM instances across service boundaries.

- **Data flow:** `Repository (ORM Model)` ➔ `Service Logic` ➔ `Public Interface (Pydantic Schema)`.

### Rule 4: Domain-Agnostic Shared Kernel (`backend/core/`)
`backend/core/` is strictly for infrastructure utilities:
- Base Pydantic models and timestamp mixins.

**No domain logic, business rules, or domain entities may live in `backend/core/`.**

### Rule 5: Client Interface Adapters (In-Process vs. Standalone Network)
When one service requires data from another, it accesses it via an adapter interface (e.g. `LibraryClient`).
- **In-process (monolith mode):** calls the service layer directly in Python memory.
- **Microservice (distributed mode):** calls the service via HTTP (`httpx`) without changing the caller's business logic.

### Rule 6: Automated Boundary Verification
Boundary rules are continuously enforced via automated architecture tests in `tests/test_architecture_boundaries.py`. Any attempt to import private internals (`*.models`, `*.repository`) across services will fail CI builds.

---

## 5. Development & Running

### Unified Local Development
Start both backend API and Streamlit frontend:
```bash
python main.py
```

Run backend only:
```bash
python main.py --backend-only
# API Swagger Docs available at: http://127.0.0.1:8000/docs
```
