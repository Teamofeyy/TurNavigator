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

## API documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

Raw OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

Export the generated OpenAPI schema to `docs/openapi.json`:

```bash
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.export_openapi
```

## Current API

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/cities
curl http://127.0.0.1:8000/cities/6
curl "http://127.0.0.1:8000/cities/6/pois?category=food"
curl http://127.0.0.1:8000/pois/6005
```
