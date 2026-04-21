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

### `GET /cities`

Returns all cities available in the current MVP seed dataset.

Example:

```bash
curl http://127.0.0.1:8000/cities
```

Each city contains `pois_count`, so the frontend can show how many objects are available before opening the city.

### `GET /cities/{city_id}`

Returns one city by internal id.

Example:

```bash
curl http://127.0.0.1:8000/cities/6
```

If the city does not exist, the API returns `404`.

### `GET /cities/{city_id}/pois`

Returns points of interest for a city.

Supported query parameters:

- `category` - optional normalized category filter, for example `food` or `history`;
- `limit` - maximum number of objects to return, from 1 to 100;
- `offset` - number of objects to skip.

Example:

```bash
curl "http://127.0.0.1:8000/cities/6/pois?category=food"
```

### `GET /pois/{poi_id}`

Returns one point of interest by internal id.

Example:

```bash
curl http://127.0.0.1:8000/pois/6005
```

If the point of interest does not exist, the API returns `404`.
