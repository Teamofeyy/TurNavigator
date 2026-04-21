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
