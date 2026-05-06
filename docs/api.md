# API Documentation

TravelContext exposes a FastAPI backend. The contract is described both by route code and by generated OpenAPI, so `docs/openapi.json` should be treated as the source of truth for field-level schemas.

## Interactive documentation

After starting the backend:

```text
http://127.0.0.1:8000/docs
```

Also available:

```text
http://127.0.0.1:8000/redoc
http://127.0.0.1:8000/openapi.json
```

## Export OpenAPI

From the `backend` directory:

```bash
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.export_openapi
```

The command rewrites `docs/openapi.json`.

## Endpoint groups

### `GET /health`

Basic availability check.

Example:

```bash
curl http://127.0.0.1:8000/health
```

### `GET /cities`

Returns all supported cities from the catalog.

Each city contains `pois_count`, so the frontend can show how rich the local catalog is before planning starts.

### `GET /cities/{city_id}`

Returns one city by internal id.

### `GET /cities/{city_id}/pois`

Returns POI cards for the selected city.

Supported query parameters:

- `category` - optional normalized category filter such as `food`, `culture`, or `accommodation`;
- `limit` - maximum number of objects to return, from `1` to `250`;
- `offset` - number of objects to skip.

POI responses include:

- planning attributes: `estimated_price_level`, `average_cost_rub`, `estimated_visit_minutes`;
- quality attributes: `popularity_score`, `data_quality_score`, `data_freshness_days`;
- enrichment metadata: `interests`, `interest_source`, Wikipedia/Wikidata/Wikimedia fields;
- media and provenance: `primary_image`, `images`, `source_links`.

### `GET /pois/{poi_id}`

Returns one point of interest by internal id.

## Reusable profiles

### `POST /profiles`

Creates a persisted MVP profile of the user's "digital consciousness 2.0".

The profile stores:

- `profile_name`;
- stable interests and budget/pace preferences;
- `goals`, `must_have`, `avoid`;
- `compromise_strategy`, `trust_level`;
- `accessibility_needs`, `preferred_time_windows`.

Example:

```bash
curl -X POST http://127.0.0.1:8000/profiles \
  -H 'Content-Type: application/json' \
  -d '{
    "profile_name": "Гастро-выходные",
    "interests": ["food", "culture"],
    "budget_level": "medium",
    "max_budget": 12000,
    "pace": "moderate",
    "max_walking_distance_km": 8,
    "preferred_transport": "walking",
    "explanation_level": "detailed",
    "goals": ["discover_local_culture"],
    "must_have": ["river_view", "coffee_break"],
    "avoid": ["stairs"],
    "compromise_strategy": "balanced",
    "trust_level": "medium",
    "accessibility_needs": ["quiet_places"],
    "preferred_time_windows": ["morning", "evening"]
  }'
```

### `GET /profiles`

Returns the most recent saved profiles for reuse in frontend MVP flows.

### `GET /profiles/{profile_id}`

Returns one saved profile by id.

### `PATCH /profiles/{profile_id}`

Updates selected profile fields without a full account system.

MVP note:

- `/profiles` endpoints are currently demo endpoints without user auth;
- in production they should be protected by at least API key or user/session auth.

## Trip planning flow

### `POST /trip-requests`

Creates a persisted planning request.

You must provide exactly one of:

- `profile_id` to reuse an existing saved profile;
- `profile` to create and persist an inline profile first.

The request also stores:

- trip duration;
- `selected_interests` for the current run;
- trip-level `constraints`;
- `start_location` and `end_location`, for example a selected hotel.

Example:

```bash
curl -X POST http://127.0.0.1:8000/trip-requests \
  -H 'Content-Type: application/json' \
  -d '{
    "city_id": 6,
    "profile_id": 1,
    "days_count": 2,
    "daily_time_limit_hours": 8,
    "selected_interests": ["food", "culture"],
    "constraints": {
      "include_accommodation": false,
      "return_to_start": true
    },
    "start_location": {
      "address": "ул. Большая Садовая, 115",
      "latitude": 47.223,
      "longitude": 39.718,
      "name": "Отель",
      "poi_id": 6001
    },
    "end_location": {
      "address": "ул. Большая Садовая, 115",
      "latitude": 47.223,
      "longitude": 39.718,
      "name": "Отель",
      "poi_id": 6001
    }
  }'
```

### `POST /recommendations/generate`

Generates a ranked list of recommendations for an existing `trip_request`.

Base scoring factors:

- interest match;
- budget fit;
- route convenience;
- pace fit;
- popularity;
- data quality.

Additional profile-aware adjustments:

- boost `must_have`;
- penalize `avoid`;
- shift base weights by `compromise_strategy`;
- change exploratory freedom by `trust_level`;
- favor categories relevant to `goals`;
- account for `accessibility_needs`;
- account for `preferred_time_windows`.

Response payload includes:

- normalized `score` and `rank`;
- `matched_interests`;
- factor breakdown;
- constraint status;
- natural-language explanation reflecting the profile context.

### `POST /routes/build`

Creates a persisted route plan for an existing `trip_request`.

If `poi_ids` are omitted, the backend first generates recommendations and then uses top candidates for routing.

The route builder estimates:

- leg distance and travel time;
- visit time;
- total time and budget;
- fit against trip constraints;
- return leg back to `end_location`.

When `strict_constraints=true`, the builder now checks the candidate point together with the projected return leg to the hotel/final point before adding it to the route.

### `GET /routes/{route_id}`

Returns a persisted route plan by id.

## Feedback and decision logging

### `POST /feedback`

Stores route feedback and appends a new decision log event.

### `GET /decision-logs`

Returns recent persisted decision log entries.

Snapshots can include:

- trip input context;
- profile snapshot;
- recommendation snapshot;
- route snapshot;
- explanation snapshot;
- feedback snapshot.

MVP note:

- `/decision-logs` is currently a demo/admin endpoint for supervision and research;
- production rollout should protect it with API key or role-based auth and add retention/delete policies.
