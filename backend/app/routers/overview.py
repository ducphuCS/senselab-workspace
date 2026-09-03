"""Overview service and home dashboard endpoint."""

from fastapi import APIRouter

from backend.app.data import SUMMARY

router = APIRouter(prefix="/api/overview", tags=["Overview"])


@router.get("", response_model=dict)
@router.get("/", response_model=dict, include_in_schema=False)
def get_overview() -> dict:
    """Data for the overview page (metrics, groups, recent activity)."""
    return SUMMARY
