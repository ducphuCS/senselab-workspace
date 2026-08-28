"""Public schemas / DTOs for the Lab service."""

from typing import Literal
from pydantic import Field
from backend.core.base_model import SchemaBase, TimestampMixin


class SampleBase(SchemaBase):
    sample_code: str = Field(..., description="Internal sample identifier, e.g. Recipe-A")
    description: str | None = None


class SampleServingItem(SchemaBase):
    blind_code: str = Field(..., description="3-digit random blind code")
    sample_code: str
    serving_order: int


class ServingPlan(SchemaBase):
    panelist_id: str
    items: list[SampleServingItem]


class TestSessionBase(SchemaBase):
    experiment_id: str
    method_id: str = Field(..., description="Reference to Library TestMethod ID")
    attribute_set_id: str | None = Field(None, description="Reference to Library AttributeSet ID")
    status: Literal["draft", "ready", "running", "completed"] = "draft"


class TestSessionRead(TestSessionBase, TimestampMixin):
    id: str
    serving_plans: list[ServingPlan] = Field(default_factory=list)


class ExperimentBase(SchemaBase):
    title: str
    description: str | None = None
    project_id: str | None = None
    status: Literal["planned", "active", "completed"] = "planned"


class ExperimentRead(ExperimentBase, TimestampMixin):
    id: str
    test_ids: list[str] = Field(default_factory=list)
