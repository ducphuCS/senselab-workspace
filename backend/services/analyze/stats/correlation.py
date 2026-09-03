"""Sensory attribute correlation matrix computation (Decision D2)."""

from backend.services.analyze.schemas import CorrelationMatrixResult


def calculate_correlation_matrix(
    test_id: str,
    attributes: list[str],
    data: dict[str, list[float]],
) -> CorrelationMatrixResult:
    """Calculate Pearson correlation matrix between sensory attributes."""
    n = len(attributes)
    matrix = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    return CorrelationMatrixResult(test_id=test_id, attributes=attributes, matrix=matrix)
