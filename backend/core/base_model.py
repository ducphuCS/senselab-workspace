"""Base models and shared schema mixins for Compusense services."""

from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SchemaBase(BaseModel):
    """Base Pydantic schema for all DTOs."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Timestamp mixin for entities tracking creation and update times."""

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
