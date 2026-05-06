# ТравелКонтекст

Прототип интеллектуальной системы поддержки планирования путешествий с учетом пользовательского контекста и ресурсных ограничений.

## Docker

Полный стек теперь можно поднять одной командой: `postgres + backend + frontend + caddy`.

```bash
cp .env.example .env
docker compose up --build -d
```

По умолчанию приложение доступно через Caddy:

```text
https://localhost:8443
```

HTTP редирект и TLS обслуживает Caddy, backend и frontend остаются во внутренней Docker-сети. Для локального запуска pgAdmin:

```bash
docker compose --profile tools up -d pgadmin
```

Прод-сборка для VDS вынесена в `compose.production.yaml`: она использует уже опубликованные образы из Docker Hub и тот же `deploy/caddy/Caddyfile`.

## Quality Gates

Локальные проверки перед коммитом теперь запускаются через `pre-commit`, а CI повторяет тот же набор хуков:

```bash
cd backend
UV_CACHE_DIR=../.uv-cache uv sync --all-groups
UV_CACHE_DIR=../.uv-cache uv run pre-commit install --config ../.pre-commit-config.yaml --install-hooks
```

Что проверяется до коммита:

- `ruff check` для backend;
- `eslint` для frontend;
- `tsc --noEmit` для frontend;
- базовые YAML/whitespace/merge-conflict проверки.

CI/CD находится в [`.github/workflows/ci-cd.yml`](/Users/teamofey/magistr-diploma/.github/workflows/ci-cd.yml). Pipeline сначала гоняет quality-проверки и frontend build, затем собирает Docker-образы, публикует их в Docker Hub и по SSH обновляет `compose.production.yaml` на VDS.

## Backend

Backend находится в папке `backend` и использует FastAPI + uv.

Для локальной базы данных теперь используется PostgreSQL в Docker на официальном образе `postgres:18.3`.
По умолчанию проектная база публикуется на `127.0.0.1:54329`, чтобы не конфликтовать с уже установленным локальным PostgreSQL на `5432`.

Для будущего импорта POI из внешних источников можно подготовить env-файл:

```bash
cd backend
cp .env.example .env.local
```

Поднять PostgreSQL:

```bash
docker compose up -d postgres
```

Применить миграции:

```bash
cd backend
UV_CACHE_DIR=../.uv-cache uv run alembic upgrade head
```

Загрузить текущие seed-данные в PostgreSQL:

```bash
cd backend
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.seed_database
```

### Запуск

```bash
cd backend
UV_CACHE_DIR=../.uv-cache uv run uvicorn app.main:app --reload
```

После запуска API доступен по адресу:

```text
http://127.0.0.1:8000
```

Проверка состояния:

```bash
curl http://127.0.0.1:8000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

Текущие API endpoint'ы:

```text
GET /health
GET /cities
GET /cities/{city_id}
GET /cities/{city_id}/pois
GET /pois/{poi_id}
POST /trip-requests
POST /recommendations/generate
POST /routes/build
GET /routes/{route_id}
POST /feedback
GET /decision-logs
```

Полезные backend-команды:

```bash
cd backend
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.export_openapi
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.seed_enrichment_report
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.catalog_quality_report
UV_CACHE_DIR=../.uv-cache uv run python -m app.tools.import_city_catalog --city-id 1 --target-count 100 --limit 180
UV_CACHE_DIR=../.uv-cache uv run alembic revision --autogenerate -m "describe change"
```

Документы по данным и ETL:

- `docs/implementation-report.md`
- `docs/api.md`
- `docs/data-ingestion-plan.md`

Ключи и внешние сервисы:

- `OPENTRIPMAP_API_KEY` - нужен для импорта популярных туристических POI и preview-данных.
- `OVERPASS_ENDPOINT` - ключ не нужен.
- `WIKIPEDIA_LANGUAGE` - ключ не нужен.
- `OPENROUTESERVICE_API_KEY` - опционален, нужен только для дорожной геометрии маршрутов на карте во frontend.

## Frontend

Frontend находится в папке `frontend` и использует Next.js 16 + React 19 + Tailwind CSS v4 + shadcn/ui.

### Переменные окружения

При необходимости можно указать адрес backend API:

```bash
cd frontend
cp .env.example .env.local
```

По умолчанию используется:

```text
http://127.0.0.1:8000
```

### Запуск

```bash
cd frontend
npm run dev
```

После запуска frontend доступен по адресу:

```text
http://127.0.0.1:3000
```

Что уже есть на frontend:

- экран планирования поездки;
- выбор города, интересов, бюджета, темпа и транспорта;
- запуск полного backend-сценария:
  - создание trip request;
  - генерация рекомендаций;
  - построение маршрута;
- отображение рекомендаций и маршрутного плана.
