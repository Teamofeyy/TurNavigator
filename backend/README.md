# Backend

FastAPI backend for the intelligent travel planning DSS prototype.

## Run locally

1. Start PostgreSQL in Docker from the project root:

```bash
docker compose up -d postgres
```

2. Prepare backend environment variables:

```bash
cp .env.example .env.local
```

3. Run Alembic migrations:

```bash
UV_CACHE_DIR=../.uv-cache uv run alembic upgrade head
```

4. Optionally load current seed cities and POI into PostgreSQL:

```bash
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.seed_database
```

5. Start the API:

```bash
uv run uvicorn app.main:app --reload
```

Optional environment file for future POI import and enrichment:

```bash
cp .env.example .env.local
```

External services and API keys:

- `OPENTRIPMAP_API_KEY` - required for importing popular tourist POI with richer descriptions and previews.
- `OVERPASS_ENDPOINT` - no API key required.
- `WIKIPEDIA_LANGUAGE` - no API key required, just selects the summary language.

Separately, on the frontend map side:

- `OPENROUTESERVICE_API_KEY` is optional and only needed if you want road-network route geometry instead of a simple polyline.

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

Build a quick enrichment coverage report for current seed POI:

```bash
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.seed_enrichment_report
```

Build a PostgreSQL catalog quality report per city:

```bash
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.catalog_quality_report
```

Import external POI into PostgreSQL for one city:

```bash
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.import_city_catalog --city-id 1 --target-count 100 --limit 180
```

Import for all cities:

```bash
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.import_city_catalog --all --target-count 100 --limit 180
```

Notes:

- without `OPENTRIPMAP_API_KEY`, the command falls back to Overpass-only import;
- with `OPENTRIPMAP_API_KEY`, the catalog can grow much faster toward `100+` quality POI per city;
- use `--skip-wikimedia` when you want a faster first pass without photo/summary enrichment.

Generate a new Alembic revision after model changes:

```bash
UV_CACHE_DIR=../.uv-cache uv run alembic revision --autogenerate -m "describe change"
```

## Current API

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/cities
curl http://127.0.0.1:8000/cities/6
curl "http://127.0.0.1:8000/cities/6/pois?category=food"
curl http://127.0.0.1:8000/pois/6005
curl -X POST http://127.0.0.1:8000/trip-requests \
  -H 'Content-Type: application/json' \
  -d '{"city_id":6,"profile":{"interests":["food","history","walking"],"budget_level":"medium","max_budget":5000,"pace":"moderate","max_walking_distance_km":8,"preferred_transport":"walking","explanation_level":"detailed"},"days_count":1,"daily_time_limit_hours":8}'
curl -X POST http://127.0.0.1:8000/recommendations/generate \
  -H 'Content-Type: application/json' \
  -d '{"trip_request_id":1,"limit":5}'
curl -X POST http://127.0.0.1:8000/routes/build \
  -H 'Content-Type: application/json' \
  -d '{"trip_request_id":1,"max_points":5,"optimize_order":true,"strict_constraints":true}'
curl http://127.0.0.1:8000/routes/1
curl -X POST http://127.0.0.1:8000/feedback \
  -H 'Content-Type: application/json' \
  -d '{"trip_request_id":1,"route_id":1,"rating":5,"comment":"Отлично"}'
curl "http://127.0.0.1:8000/decision-logs?limit=10"
```
