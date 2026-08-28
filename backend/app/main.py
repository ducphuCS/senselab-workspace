"""Compusense backend microservice (FastAPI Gateway / Hub)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import summary
from backend.services.library import router as library_router
from backend.services.lab import router as lab_router
from backend.services.ballot import router as ballot_router
from backend.services.analytics import router as analytics_router

app = FastAPI(
    title="Compusense Backend",
    version="0.1.0",
    description="Sensory Lab Workspace Backend & Microservices Hub",
)

# Dev-only CORS: allow the Streamlit frontend to reach this service.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Summary & Health Check
app.include_router(summary.router)

# Domain Microservice Routers
app.include_router(library_router)
app.include_router(lab_router)
app.include_router(ballot_router)
app.include_router(analytics_router)


@app.get("/api/health")
def health() -> dict:
    """Liveness check used by the frontend bridge."""
    return {"status": "ok"}
