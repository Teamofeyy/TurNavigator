# ТравелКонтекст

Прототип интеллектуальной системы поддержки планирования путешествий с учетом пользовательского контекста и ресурсных ограничений.

## Backend

Backend находится в папке `backend` и использует FastAPI + uv.

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
```

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
