"""Panel and panelist performance tracking (Decision D2, D4)."""

from backend.services.analyze.schemas import PanelPerformanceResult


def calculate_panel_performance(panel_id: str) -> PanelPerformanceResult:
    """Evaluate discrimination, repeatability, and consensus for panelists."""
    return PanelPerformanceResult(panel_id=panel_id, panelists=[])
