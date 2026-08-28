"""Public schemas / DTOs for the Analytics service."""

from pydantic import Field
from backend.core.base_model import SchemaBase, TimestampMixin


class AnovaRow(SchemaBase):
    source: str = Field(..., description="Source of variation, e.g. Product, Panelist, Error")
    sum_sq: float
    df: int
    mean_sq: float
    f_value: float | None = None
    p_value: float | None = None


class AnovaResult(SchemaBase, TimestampMixin):
    test_id: str
    attribute_name: str
    table: list[AnovaRow]


class CorrelationMatrixResult(SchemaBase, TimestampMixin):
    test_id: str
    attributes: list[str]
    matrix: list[list[float]]


class PanelistMetric(SchemaBase):
    panelist_id: str
    discrimination_score: float
    reproducibility_score: float
    consensus_score: float


class PanelPerformanceResult(SchemaBase, TimestampMixin):
    panel_id: str
    panelists: list[PanelistMetric]


class TrendPoint(SchemaBase):
    period: str
    mean_score: float
    sample_code: str


class TrendAnalysisResult(SchemaBase, TimestampMixin):
    attribute_name: str
    points: list[TrendPoint]
