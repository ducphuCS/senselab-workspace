"""Analyze service API endpoints."""

from fastapi import APIRouter
from backend.services.analyze.schemas import (
    AnovaResult,
    CorrelationMatrixResult,
    PanelPerformanceResult,
    TrendAnalysisResult,
)
from backend.services.analyze.stats import (
    anova,
    correlation,
    performance,
    trends,
)

router = APIRouter(prefix="/api/v1/analyze", tags=["Analyze"])


@router.get("/anova/{test_id}", response_model=AnovaResult)
def get_anova(test_id: str, attribute: str = "Overall") -> AnovaResult:
    """Get ANOVA table for a test session attribute."""
    return anova.calculate_one_way_anova(test_id, attribute, {})


@router.get("/correlations/{test_id}", response_model=CorrelationMatrixResult)
def get_correlations(test_id: str) -> CorrelationMatrixResult:
    """Get attribute correlation matrix for a test session."""
    return correlation.calculate_correlation_matrix(test_id, [], {})


@router.get("/panel-performance/{panel_id}", response_model=PanelPerformanceResult)
def get_panel_performance(panel_id: str) -> PanelPerformanceResult:
    """Get performance metrics for a sensory panel."""
    return performance.calculate_panel_performance(panel_id)


@router.get("/trends/{attribute_name}", response_model=TrendAnalysisResult)
def get_attribute_trends(attribute_name: str) -> TrendAnalysisResult:
    """Get longitudinal trends for an attribute."""
    return trends.calculate_attribute_trends(attribute_name)
