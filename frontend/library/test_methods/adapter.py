"""API Adapter for Library → Test Methods page."""

from __future__ import annotations

from typing import Any
from main import api_delete, api_get, api_post, api_put, backend_healthy


class TestMethodsAPI:
    """Client wrapper for Library Test Methods endpoints."""

    @staticmethod
    def is_healthy() -> bool:
        return backend_healthy()

    @staticmethod
    def list_methods(
        category: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if category and category != "all":
            params["category"] = category
        if status and status != "all":
            params["status"] = status
        if search:
            params["search"] = search
        return api_get("/api/library/methods", params=params)

    @staticmethod
    def get_method(method_id: str) -> dict[str, Any]:
        return api_get(f"/api/library/methods/{method_id}")

    @staticmethod
    def create_method(payload: dict[str, Any]) -> dict[str, Any]:
        return api_post("/api/library/methods", payload=payload)

    @staticmethod
    def update_method(method_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return api_put(f"/api/library/methods/{method_id}", payload=payload)

    @staticmethod
    def delete_method(method_id: str) -> dict[str, Any]:
        return api_delete(f"/api/library/methods/{method_id}")

    @staticmethod
    def archive_method(method_id: str) -> dict[str, Any]:
        return api_post(f"/api/library/methods/{method_id}/archive")

    @staticmethod
    def duplicate_method(method_id: str, new_name: str | None = None) -> dict[str, Any]:
        payload = {"new_name": new_name} if new_name else None
        return api_post(f"/api/library/methods/{method_id}/duplicate", payload=payload)

    @staticmethod
    def add_preset(method_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return api_post(f"/api/library/methods/{method_id}/presets", payload=payload)

    @staticmethod
    def get_preset(preset_id: str) -> dict[str, Any]:
        return api_get(f"/api/library/presets/{preset_id}")

    @staticmethod
    def update_preset(preset_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return api_put(f"/api/library/presets/{preset_id}", payload=payload)

    @staticmethod
    def delete_preset(preset_id: str) -> dict[str, Any]:
        return api_delete(f"/api/library/presets/{preset_id}")

    @staticmethod
    def archive_preset(preset_id: str) -> dict[str, Any]:
        return api_post(f"/api/library/presets/{preset_id}/archive")
