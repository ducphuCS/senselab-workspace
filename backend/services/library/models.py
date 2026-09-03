"""Private domain models and records for the Library service."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PresetRecord:
    """Private representation of a Test Method Preset."""

    id: str
    test_method_id: str
    name: str
    description: str | None
    prerequisites_json: str
    output_schema_json: str
    is_default: bool
    status: str
    usage_count: int
    created_at: datetime
    updated_at: datetime


@dataclass
class TestMethodRecord:
    """Private representation of a Sensory Test Method."""

    id: str
    name: str
    category: str
    description: str | None
    procedure_json: str
    assumptions_json: str
    derived_from_id: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    presets: list[PresetRecord] = field(default_factory=list)
