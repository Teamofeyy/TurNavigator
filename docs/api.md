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

### `POST /trip-requests`

Creates an in-memory trip planning request.

Example:

```bash
curl -X POST http://127.0.0.1:8000/trip-requests \
  -H 'Content-Type: application/json' \
  -d '{"city_id":6,"profile":{"interests":["food","history","walking"],"budget_level":"medium","max_budget":5000,"pace":"moderate","max_walking_distance_km":8,"preferred_transport":"walking","explanation_level":"detailed"},"days_count":1,"daily_time_limit_hours":8}'
```

The response contains a generated `id`. Use this id as `trip_request_id` when generating recommendations.

### `POST /recommendations/generate`

Generates a ranked list of personalized recommendations for an existing trip request.

Scoring factors:

- interest match;
- budget fit;
- route convenience;
- pace fit;
- popularity;
- data quality.

Example:

```bash
curl -X POST http://127.0.0.1:8000/recommendations/generate \
  -H 'Content-Type: application/json' \
  -d '{"trip_request_id":1,"limit":5}'
```

The response includes `score`, `rank`, `matched_interests`, factor values, constraint statuses, and a human-readable explanation for each recommended POI.

### `POST /routes/build`

Builds an ordered route for an existing trip request.

If `poi_ids` are omitted, the backend first generates recommendations and then turns the top candidates into a route. The route builder estimates:

- distance between points;
- movement time;
- visit time;
- total time;
- estimated budget;
- whether the route fits user constraints.

Example:

```bash
curl -X POST http://127.0.0.1:8000/routes/build \
  -H 'Content-Type: application/json' \
  -d '{"trip_request_id":1,"max_points":5,"optimize_order":true,"strict_constraints":true}'
```

### `GET /routes/{route_id}`

Returns a previously built in-memory route plan.

Example:

```bash
curl http://127.0.0.1:8000/routes/1
```
