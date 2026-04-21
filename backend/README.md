# Backend

FastAPI backend for the intelligent travel planning DSS prototype.

## Run locally

```bash
uv run uvicorn app.main:app --reload
```

## Health check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```
