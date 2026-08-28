# Backend Architecture Specification

This document defines the backend architecture for the **Compusense Sensory Lab Workspace**, implementing a **Modular Service Architecture (Microservice-Ready Monolith)**.

---

## 1. Architecture Overview

The backend is structured into **4 isolated domain services** coordinated through an API Gateway / Application Hub. Each service is fully encapsulated with its own schemas, domain logic, data access, and API routers.

```
                              ┌─────────────────────────────┐
                              │  Frontend (Streamlit / QR)  │
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
 │   Library Service   │       │  Lab Service  │ │  Ballot Service   │ │  Analytics Service  │
 │  /api/v1/library    │       │  /api/v1/lab  │ │  /api/v1/ballots  │ │ /api/v1/analytics   │
 ├─────────────────────┤       ├───────────────┤ ├───────────────────┤ ├─────────────────────┤
 │ • Test Methods      │       │ • Experiments │ │ • QR / Link entry │ │ • ANOVA tables      │
 │ • Attribute Sets    │       │ • Tests       │ │ • In-app ballots  │ │ • Correlation matrix│
 │ • Panel Registry    │       │ • Blind codes │ │ • Live responses  │ │ • Panel performance │
 │ • Panelists         │       │ • Servings    │ │ • Validation      │ │ • Sensory trends    │
 └─────────────────────┘       └───────────────┘ └───────────────────┘ └─────────────────────┘
```

---

## 2. Bounded Context Services

| Service | Route Prefix | Primary Responsibilities | Domain Entities |
|---|---|---|---|
| **Library** | `/api/v1/library` | Master registry for pre-test configurations | `TestMethod`, `AttributeSet`, `Attribute`, `Panel`, `Panelist` |
| **Lab** | `/api/v1/lab` | Experiment lifecycle, test sessions, blind 3-digit coding, serving order randomization | `Project`, `Experiment`, `TestSession`, `Sample`, `ServingPlan` |
| **Ballot** | `/api/v1/ballots` | Real-time panelist response collection via tokenized QR/link (no auth friction) | `BallotSession`, `ScaleResponse`, `Submission` |
| **Analytics** | `/api/v1/analytics` | Statistical & numerical compute engine (NumPy, SciPy, Statsmodels) | ANOVA tables, Correlation matrices, Panel discrimination & consensus, Trends |
| **Gateway / Summary** | `/api/v1/summary`, `/api/health` | Root router, cross-service metric aggregation, health checks | Cross-service summary aggregates |

---

## 3. Directory Layout

```
backend/
├── app/
│   ├── main.py                  # API Gateway / Application Hub (mounts service routers)
│   ├── config.py                # Global settings & environment configuration
│   └── middleware.py            # CORS, error handling, request logging
├── core/                        # Domain-agnostic shared infrastructure only
│   ├── db.py                    # Database connection factory & session dependency
│   ├── base_model.py            # Base declarative models / common schema mixins
│   └── security.py              # QR / Ballot token hashing & verification
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
│   ├── ballot/                  # === Ballot Service ===
│   │   ├── __init__.py
│   │   ├── router.py            # Endpoints: /api/v1/ballots/*
│   │   ├── models.py            # (Private) ORM database models
│   │   ├── schemas.py           # (Public) Pydantic schemas / DTOs
│   │   └── repository.py        # (Private) Database access layer
│   │
│   └── analytics/               # === Analytics Engine ===
│       ├── __init__.py
│       ├── router.py            # Endpoints: /api/v1/analytics/*
│       ├── schemas.py           # (Public) Pydantic schemas / DTOs
│       └── stats/               # Numerical & statistical computation
│           ├── anova.py         # One-way, Two-way ANOVA computation
│           ├── correlation.py   # Pearson / Spearman correlation matrices
│           ├── performance.py   # Panelist discrimination & agreement scores
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
from backend.services.library.repository import PanelistRepository
from backend.services.library.models import PanelistORM

# ✅ CORRECT: Lab interacts only with public schemas or public client interfaces
from backend.services.library.schemas import PanelistRead
from backend.services.library.client import LibraryClient
```

### Rule 2: References by Identifier Only (No Cross-Domain ORM Relationships)
Never define ORM foreign keys or table joins (`relationship()`) across domain service boundaries. Use scalar IDs (`str` or `int`).

```python
# ❌ VIOLATION: Direct ORM relationship across service boundaries
class TestSession(Base):
    __tablename__ = "test_sessions"
    id: str = Column(String, primary_key=True)
    panelist: PanelistORM = relationship("PanelistORM")  # Direct cross-domain DB binding!

# ✅ CORRECT: Scalar ID reference only
class TestSession(Base):
    __tablename__ = "test_sessions"
    id: str = Column(String, primary_key=True)
    panelist_id: str = Column(String, index=True)  # ID reference; resolved via service contract
```

### Rule 3: Exchange DTOs (Pydantic Schemas), Never Raw ORM Instances
Services must communicate strictly using serialized Data Transfer Objects (Pydantic schemas). Never pass active SQLAlchemy/SQLModel database sessions or un-serialized ORM instances across service boundaries.

- **Data flow:** `Repository (ORM Model)` ➔ `Service Logic` ➔ `Public Interface (Pydantic Schema)`.

### Rule 4: Domain-Agnostic Shared Kernel (`backend/core/`)
`backend/core/` is strictly for infrastructure utilities:
- Database engine setup and session dependency providers.
- Base Pydantic models and timestamp mixins.
- Cryptographic / QR token utilities.

**No domain logic, business rules, or domain entities may live in `backend/core/`.**

### Rule 5: Client Interface Adapters (In-Process vs. Standalone Network)
When one service requires data from another, it accesses it via an adapter interface (e.g. `LibraryClient`).
- **In-process (monolith mode):** calls the service layer directly in Python memory.
- **Microservice (distributed mode):** calls the service via HTTP (`httpx`) without changing the caller's business logic.

```python
# backend/services/library/client.py
class LibraryClient(Protocol):
    def get_panelist(self, panelist_id: str) -> PanelistRead | None: ...

class LocalLibraryClient:
    def get_panelist(self, panelist_id: str) -> PanelistRead | None:
        return library_service.get_panelist(panelist_id)

class HttpLibraryClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_panelist(self, panelist_id: str) -> PanelistRead | None:
        response = httpx.get(f"{self.base_url}/api/v1/library/panelists/{panelist_id}")
        return PanelistRead.model_validate(response.json()) if response.is_success else None
```

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
