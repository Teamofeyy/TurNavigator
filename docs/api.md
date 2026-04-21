# API Documentation

The backend uses FastAPI, so OpenAPI documentation is generated automatically from route definitions, Pydantic response schemas, descriptions, examples, and tags.

## Interactive Documentation

After starting the backend, open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI is available at `/docs`.

ReDoc is available at:

```text
http://127.0.0.1:8000/redoc
```

The raw OpenAPI schema is available at:

```text
http://127.0.0.1:8000/openapi.json
```

## Export OpenAPI Schema

From the `backend` directory:

```bash
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.export_openapi
```

The command writes the generated schema to:

```text
docs/openapi.json
```

## Current Endpoints

### `GET /health`

Checks whether the backend API is available.

Response:

```json
{
  "status": "ok"
}
```

The endpoint is tagged as `health` in the generated OpenAPI schema.
