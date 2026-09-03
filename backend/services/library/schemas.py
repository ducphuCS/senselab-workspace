"""Public schemas / DTOs for the Library service."""

from __future__ import annotations

from typing import Any, Literal
from pydantic import Field
from backend.core.base_model import SchemaBase, TimestampMixin

MethodCategory = Literal["discrimination", "descriptive", "hedonic"]
EntityStatus = Literal["draft", "active", "archived"]


# ---------------------------------------------------------------------------
# Prerequisites & Output Schemas for Test Methods & Presets
# ---------------------------------------------------------------------------


class InputRequirements(SchemaBase):
    """Input requirements pre-filling Lab test setup."""

    default_panelist_count: int | None = Field(
        default=None, description="Recommended panelist count"
    )
    default_sample_count: int | None = Field(
        default=None, description="Default number of samples evaluated"
    )
    presentation_format: str | None = Field(
        default=None,
        description="Sample presentation scheme",
    )
    custom_parameters: dict[str, Any] = Field(
        default_factory=dict, description="Custom parameters"
    )


class InstructionalConditions(SchemaBase):
    """Environmental and instructional conditions for technician setup."""

    lighting: str | None = Field(
        default=None, description="Sensory booth lighting"
    )
    temperature: str | None = Field(
        default=None, description="Booth and sample serving temperature"
    )
    palate_cleanser: str | None = Field(
        default=None,
        description="Palate cleansing protocol",
    )
    rest_interval_seconds: int | None = Field(
        default=None, description="Forced rest interval between sample evaluations (sec)"
    )
    sample_prep_instructions: str | None = Field(
        default=None, description="Sample handling and container specifications"
    )


class PanelistEligibility(SchemaBase):
    """Panelist screening and readiness requirements."""

    qualification_level: str | None = Field(
        default=None,
        description="Required panelist qualification",
    )
    pre_test_restrictions: str | None = Field(
        default=None,
        description="Panelist pre-test instructions",
    )


class PrerequisitesSchema(SchemaBase):
    """Structured operational prerequisites grouped into distinct categories."""

    input_requirements: InputRequirements = Field(default_factory=InputRequirements)
    instructional_conditions: InstructionalConditions = Field(
        default_factory=InstructionalConditions
    )
    panelist_eligibility: PanelistEligibility = Field(
        default_factory=PanelistEligibility
    )


class OutputMetricsSchema(SchemaBase):
    """Statistical and metric output definitions produced by this method/preset."""

    primary_metric: str | None = Field(
        default=None, description="Primary outcome metric (e.g., Significant Difference)"
    )
    metrics: list[str] = Field(
        default_factory=list, description="List of recorded metrics"
    )
    statistical_test: str | None = Field(
        default=None, description="Statistical pipeline used in Analyze"
    )


# ---------------------------------------------------------------------------
# Preset Schemas
# ---------------------------------------------------------------------------


class PresetBase(SchemaBase):
    """Base schema for a Test Method Preset."""

    name: str = Field(..., description="Preset name, e.g. Standard 30-Panelist Difference")
    description: str | None = Field(default=None, description="Preset context or scope")
    prerequisites: PrerequisitesSchema = Field(default_factory=PrerequisitesSchema)
    output_schema: OutputMetricsSchema = Field(default_factory=OutputMetricsSchema)
    is_default: bool = Field(default=False, description="Whether this is the default preset")


class PresetCreate(PresetBase):
    """Schema for creating a Preset."""

    pass


class PresetUpdate(SchemaBase):
    """Schema for updating a Preset."""

    name: str | None = None
    description: str | None = None
    prerequisites: PrerequisitesSchema | None = None
    output_schema: OutputMetricsSchema | None = None
    is_default: bool | None = None
    status: EntityStatus | None = None


class PresetRead(PresetBase, TimestampMixin):
    """Public read DTO for a Preset."""

    id: str
    test_method_id: str
    status: EntityStatus = "draft"
    usage_count: int = 0


# ---------------------------------------------------------------------------
# Test Method Schemas
# ---------------------------------------------------------------------------


class TestMethodBase(SchemaBase):
    """Base schema for a Sensory Test Method."""

    name: str = Field(..., description="Method name, e.g. Triangle Test, QDA, 9-Point Hedonic")
    category: MethodCategory = Field(
        default="discrimination", description="Sensory test category"
    )
    description: str | None = Field(
        default=None, description="High-level description of the sensory test method"
    )
    procedure: list[str] = Field(
        default_factory=list, description="Ordered steps for test execution"
    )
    assumptions: list[str] = Field(
        default_factory=list, description="Theoretical and statistical assumptions"
    )


class TestMethodCreate(TestMethodBase):
    """Schema for creating a Test Method with optional initial presets."""

    initial_presets: list[PresetCreate] = Field(
        default_factory=list, description="Optional initial presets to create alongside the method"
    )


class TestMethodUpdate(SchemaBase):
    """Schema for updating a Test Method."""

    name: str | None = None
    category: MethodCategory | None = None
    description: str | None = None
    procedure: list[str] | None = None
    assumptions: list[str] | None = None
    status: EntityStatus | None = None


class TestMethodRead(TestMethodBase, TimestampMixin):
    """Public read DTO for a Test Method including its presets."""

    id: str
    derived_from_id: str | None = None
    status: EntityStatus = "draft"
    presets: list[PresetRead] = Field(default_factory=list)
    total_usage_count: int = 0


# ---------------------------------------------------------------------------
# Attributes & Panels Schemas (Preserved for Library boundary)
# ---------------------------------------------------------------------------


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
