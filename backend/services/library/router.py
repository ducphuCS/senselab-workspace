"""Library service API endpoints."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.services.library.repository import get_library_repository
from backend.services.library.schemas import (
    AttributeRead,
    AttributeSetRead,
    EntityStatus,
    MethodCategory,
    PanelRead,
    PresetCreate,
    PresetRead,
    PresetUpdate,
    TestMethodCreate,
    TestMethodRead,
    TestMethodUpdate,
)

router = APIRouter(prefix="/api/library", tags=["Library"])


class DuplicateRequest(BaseModel):
    new_name: str | None = Field(default=None, description="Optional custom name for duplicated copy")


# ---------------------------------------------------------------------------
# Test Methods Endpoints
# ---------------------------------------------------------------------------


@router.get("/methods", response_model=list[TestMethodRead])
def list_test_methods(
    category: Annotated[MethodCategory | None, Query(description="Filter by category")] = None,
    status_filter: Annotated[EntityStatus | None, Query(alias="status", description="Filter by status")] = None,
    search: Annotated[str | None, Query(description="Search by name or description")] = None,
) -> list[TestMethodRead]:
    """List registered sensory test methods with optional filters."""
    repo = get_library_repository()
    return repo.list_test_methods(category=category, status=status_filter, search=search)


@router.post("/methods", response_model=TestMethodRead, status_code=status.HTTP_201_CREATED)
def create_test_method(payload: TestMethodCreate) -> TestMethodRead:
    """Create a new sensory test method."""
    repo = get_library_repository()
    return repo.create_test_method(payload)


@router.get("/methods/{method_id}", response_model=TestMethodRead)
def get_test_method(method_id: str) -> TestMethodRead:
    """Get a sensory test method by its unique ID."""
    repo = get_library_repository()
    method = repo.get_test_method(method_id)
    if not method:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test method '{method_id}' not found.")
    return method


@router.put("/methods/{method_id}", response_model=TestMethodRead)
def update_test_method(method_id: str, payload: TestMethodUpdate) -> TestMethodRead:
    """Update a sensory test method (guarded against destructive edits if in use)."""
    repo = get_library_repository()
    try:
        return repo.update_test_method(method_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/methods/{method_id}", status_code=status.HTTP_200_OK)
def delete_test_method(method_id: str) -> dict[str, str]:
    """Hard-delete an unused draft test method."""
    repo = get_library_repository()
    try:
        repo.delete_test_method(method_id)
        return {"status": "deleted", "id": method_id}
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/methods/{method_id}/archive", response_model=TestMethodRead)
def archive_test_method(method_id: str) -> TestMethodRead:
    """Archive a test method and all its child presets."""
    repo = get_library_repository()
    try:
        return repo.archive_test_method(method_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/methods/{method_id}/duplicate", response_model=TestMethodRead, status_code=status.HTTP_201_CREATED)
def duplicate_test_method(method_id: str, payload: DuplicateRequest | None = None) -> TestMethodRead:
    """Duplicate an existing test method and all its presets into a fresh draft copy."""
    repo = get_library_repository()
    new_name = payload.new_name if payload else None
    try:
        return repo.duplicate_test_method(method_id, new_name=new_name)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Presets Endpoints
# ---------------------------------------------------------------------------


@router.post("/methods/{method_id}/presets", response_model=PresetRead, status_code=status.HTTP_201_CREATED)
def add_preset(method_id: str, payload: PresetCreate) -> PresetRead:
    """Add a new preset under a specific sensory test method."""
    repo = get_library_repository()
    try:
        return repo.create_preset(method_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/presets/{preset_id}", response_model=PresetRead)
def get_preset(preset_id: str) -> PresetRead:
    """Get a preset by its unique ID."""
    repo = get_library_repository()
    preset = repo.get_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Preset '{preset_id}' not found.")
    return preset


@router.put("/presets/{preset_id}", response_model=PresetRead)
def update_preset(preset_id: str, payload: PresetUpdate) -> PresetRead:
    """Update a draft preset (locked if used in tests)."""
    repo = get_library_repository()
    try:
        return repo.update_preset(preset_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/presets/{preset_id}", status_code=status.HTTP_200_OK)
def delete_preset(preset_id: str) -> dict[str, str]:
    """Delete an unused draft preset."""
    repo = get_library_repository()
    try:
        repo.delete_preset(preset_id)
        return {"status": "deleted", "id": preset_id}
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/presets/{preset_id}/archive", response_model=PresetRead)
def archive_preset(preset_id: str) -> PresetRead:
    """Archive an individual preset."""
    repo = get_library_repository()
    try:
        return repo.archive_preset(preset_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Attributes & Panels Endpoints (Placeholders preserved)
# ---------------------------------------------------------------------------


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
