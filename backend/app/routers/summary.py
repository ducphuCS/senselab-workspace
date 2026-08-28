"""Home page summary endpoint."""

from fastapi import APIRouter

from backend.app.data import SUMMARY

router = APIRouter(prefix="/api", tags=["summary"])


@router.get("/summary")
def get_summary() -> dict:
    """Data for the home page (metrics, groups, recent activity)."""
    return SUMMARY
