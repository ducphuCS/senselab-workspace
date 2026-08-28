"""Longitudinal trend analysis for sensory attributes over time (Decision D2)."""

from backend.services.analytics.schemas import TrendAnalysisResult


def calculate_attribute_trends(attribute_name: str) -> TrendAnalysisResult:
    """Analyze historical sensory trends across test sessions."""
    return TrendAnalysisResult(attribute_name=attribute_name, points=[])
