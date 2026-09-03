"""Compusense entry point — the bridge between the Streamlit frontend and the backend microservice.

Frontend pages call the ``api_*`` helpers below instead of talking to the
backend directly, so the backend URL and HTTP details live in exactly one
place. ``main()`` additionally launches the pieces for local development:

    python main.py                 # start backend + frontend together
    python main.py --frontend-only # start only the Streamlit app
    python main.py --backend-only  # start only the backend API
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

BACKEND_URL = os.environ.get("COMPUSENSE_BACKEND_URL", "http://127.0.0.1:8000")


def api_get(path: str, params: dict | None = None) -> dict:
    """Fetch JSON from the backend. Used by the frontend pages."""
    import httpx

    with httpx.Client(base_url=BACKEND_URL, timeout=10) as client:
        response = client.get(path, params=params)
        response.raise_for_status()
        return response.json()


def api_post(path: str, payload: dict | None = None) -> dict:
    """Send JSON to the backend. Used by the frontend pages."""
    import httpx

    with httpx.Client(base_url=BACKEND_URL, timeout=10) as client:
        response = client.post(path, json=payload)
        response.raise_for_status()
        return response.json()


def api_put(path: str, payload: dict | None = None) -> dict:
    """Send PUT JSON to the backend. Used by the frontend pages."""
    import httpx

    with httpx.Client(base_url=BACKEND_URL, timeout=10) as client:
        response = client.put(path, json=payload)
        response.raise_for_status()
        return response.json()


def api_delete(path: str, params: dict | None = None) -> dict:
    """Send DELETE request to the backend. Used by the frontend pages."""
    import httpx

    with httpx.Client(base_url=BACKEND_URL, timeout=10) as client:
        response = client.delete(path, params=params)
        response.raise_for_status()
        return response.json()


def backend_healthy() -> bool:
    """True if the backend answers /api/health."""
    try:
        return api_get("/api/health").get("status") == "ok"
    except Exception:
        return False


def _run_backend(port: int) -> int:
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ]
    )


def _run_frontend(port: int) -> int:
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "frontend/app.py",
            "--server.port",
            str(port),
            "--server.headless",
            "true",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compusense launcher (bridge between frontend and backend)."
    )
    parser.add_argument(
        "--backend-only", action="store_true", help="start the backend API only"
    )
    parser.add_argument(
        "--frontend-only", action="store_true", help="start the Streamlit app only"
    )
    parser.add_argument("--backend-port", type=int, default=8000)
    parser.add_argument("--frontend-port", type=int, default=8501)
    args = parser.parse_args()

    if args.backend_only and not args.frontend_only:
        raise SystemExit(_run_backend(args.backend_port))

    if args.frontend_only and not args.backend_only:
        raise SystemExit(_run_frontend(args.frontend_port))

    # Default: run both. Backend runs in the background and is stopped when
    # the Streamlit process exits.
    backend = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.backend_port),
        ]
    )
    try:
        raise SystemExit(_run_frontend(args.frontend_port))
    finally:
        backend.terminate()


if __name__ == "__main__":
    main()
