"""ANOVA computations for sensory data (Decision D2)."""

from typing import Sequence
from backend.services.analytics.schemas import AnovaResult, AnovaRow


def calculate_one_way_anova(
    test_id: str,
    attribute_name: str,
    groups: dict[str, Sequence[float]],
) -> AnovaResult:
    """Calculate one-way ANOVA table for product comparisons on a sensory attribute."""
    # Placeholder computation stub
    return AnovaResult(
        test_id=test_id,
        attribute_name=attribute_name,
        table=[
            AnovaRow(source="Product", sum_sq=0.0, df=len(groups) - 1, mean_sq=0.0, f_value=0.0, p_value=1.0),
            AnovaRow(source="Error", sum_sq=0.0, df=0, mean_sq=0.0),
        ],
    )
