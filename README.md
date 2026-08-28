# Compusense

Centralized workspace for the daily operations of a Sensory Lab.

## Run

```bash
uv sync                 # install dependencies
python main.py          # start backend (uvicorn :8000) + frontend (streamlit :8501)
```

Or run pieces separately:

```bash
python main.py --backend-only   # API only
python main.py --frontend-only  # Streamlit only
```

Open http://localhost:8501 in your browser.

## Layout

- `main.py` — bridge between the Streamlit frontend and the backend microservice
  (API client + dev launcher). Frontend pages call `api_get`/`api_post` here.
- `backend/` — FastAPI microservice (in-memory placeholder data for now).
- `frontend/` — Streamlit app; the home page lives in `frontend/app.py`.
- `docs/` — program and intention documents.

## Status

Draft: home page with metrics, workspace areas, and recent activity served via
`GET /api/summary`. Persistence, real data models, and the Overview / Library /
Lab / Analyze pages are next.
