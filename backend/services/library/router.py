"""Library service API endpoints."""

from fastapi import APIRouter
from backend.services.library.schemas import (
    PanelistRead,
    TestMethodRead,
    AttributeRead,
    AttributeSetRead,
    PanelRead,
)

router = APIRouter(prefix="/api/v1/library", tags=["Library"])


@router.get("/methods", response_model=list[TestMethodRead])
def list_test_methods() -> list[TestMethodRead]:
    """List registered sensory test methods."""
    return []


@router.get("/panelists", response_model=list[PanelistRead])
def list_panelists() -> list[PanelistRead]:
    """List registered panelists."""
    return []


@router.get("/panels", response_model=list[PanelRead])
def list_panels() -> list[PanelRead]:
    """List registered sensory panels."""
    return []


@router.get("/attributes", response_model=list[AttributeRead])
def list_attributes() -> list[AttributeRead]:
    """List individual sensory attributes."""
    return []


@router.get("/attribute-sets", response_model=list[AttributeSetRead])
def list_attribute_sets() -> list[AttributeSetRead]:
    """List attribute sets."""
    return []
