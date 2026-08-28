"""Public schemas / DTOs for the Ballot service."""

from typing import Any
from pydantic import Field
from backend.core.base_model import SchemaBase, TimestampMixin


class BallotServingItemRead(SchemaBase):
    blind_code: str
    serving_order: int


class BallotSessionRead(SchemaBase):
    token: str
    test_id: str
    panelist_name: str | None = None
    samples: list[BallotServingItemRead] = Field(default_factory=list)
    attributes: list[dict[str, Any]] = Field(default_factory=list)
    is_submitted: bool = False


class RatingSubmission(SchemaBase):
    blind_code: str
    ratings: dict[str, float | str] = Field(..., description="attribute_id / name -> rating score")


class BallotSubmissionPayload(SchemaBase):
    token: str
    submissions: list[RatingSubmission]
    comments: str | None = None


class BallotSubmissionResult(SchemaBase, TimestampMixin):
    submission_id: str
    status: str = "received"
