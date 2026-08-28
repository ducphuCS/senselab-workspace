"""Lab service API endpoints."""

from fastapi import APIRouter
from backend.services.lab.schemas import ExperimentRead, TestSessionRead

router = APIRouter(prefix="/api/v1/lab", tags=["Lab"])


@router.get("/experiments", response_model=list[ExperimentRead])
def list_experiments() -> list[ExperimentRead]:
    """List sensory experiments."""
    return []


@router.get("/tests", response_model=list[TestSessionRead])
def list_tests() -> list[TestSessionRead]:
    """List test sessions."""
    return []
