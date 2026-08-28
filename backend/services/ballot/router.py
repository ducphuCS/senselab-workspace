"""Ballot ingestion API endpoints (panelist-facing QR / token access)."""

from fastapi import APIRouter, HTTPException
from backend.services.ballot.schemas import (
    BallotSessionRead,
    BallotSubmissionPayload,
    BallotSubmissionResult,
)

router = APIRouter(prefix="/api/v1/ballots", tags=["Ballots"])


@router.get("/{token}", response_model=BallotSessionRead)
def get_ballot_session(token: str) -> BallotSessionRead:
    """Retrieve ballot details for an active sensory test session via QR/token."""
    raise HTTPException(status_code=404, detail="Ballot token not found or expired")


@router.post("/submit", response_model=BallotSubmissionResult)
def submit_ballot_response(payload: BallotSubmissionPayload) -> BallotSubmissionResult:
    """Submit panelist ratings for a test ballot."""
    return BallotSubmissionResult(submission_id="placeholder-id", status="received")
