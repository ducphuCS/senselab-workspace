"""Public schemas / DTOs for the Library service."""

from typing import Literal
from pydantic import Field
from backend.core.base_model import SchemaBase, TimestampMixin


class AttributeBase(SchemaBase):
    name: str = Field(..., description="Name of the sensory attribute (e.g., Sweetness)")
    scale_type: Literal["linear", "category", "line_scale", "ranking"] = "linear"
    min_value: float = 0.0
    max_value: float = 10.0
    unit: str | None = None
    description: str | None = None


class AttributeRead(AttributeBase, TimestampMixin):
    id: str


class AttributeSetBase(SchemaBase):
    name: str
    description: str | None = None
    attribute_ids: list[str] = Field(default_factory=list)


class AttributeSetRead(AttributeSetBase, TimestampMixin):
    id: str


class PanelBase(SchemaBase):
    name: str
    description: str | None = None


class PanelRead(PanelBase, TimestampMixin):
    id: str


class TestMethodBase(SchemaBase):
    name: str = Field(..., description="Method name, e.g. Triangle Test, QDA, Hedonic")
    category: Literal["discrimination", "descriptive", "hedonic"] = "discrimination"
    description: str | None = None


class TestMethodRead(TestMethodBase, TimestampMixin):
    id: str
