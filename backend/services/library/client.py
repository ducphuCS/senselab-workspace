"""Public client interface for accessing Library service data from other services."""

from typing import Protocol
from backend.services.library.schemas import TestMethodRead


class LibraryClient(Protocol):
    """Abstract protocol for Library data access across boundaries."""

    def get_test_method(self, method_id: str) -> TestMethodRead | None:
        """Fetch test method DTO by ID."""
        ...
