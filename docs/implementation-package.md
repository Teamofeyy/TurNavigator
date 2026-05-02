# Implementation Package

## Что входит в пакет внедрения

- Next.js frontend для выбора контекста поездки и показа маршрута;
- FastAPI backend с persisted `profiles`, `trip_requests`, `recommendation_runs`, `route_plans`, `feedback_entries`, `decision_logs`;
- PostgreSQL-схема с Alembic-миграциями;
- ETL-план по наполнению каталога городов и POI;
- базовый evaluation script для количественной оценки качества рекомендаций;
- набор smoke и service tests.

## Архитектурная схема

1. Пользователь формирует профиль и контекст поездки во frontend.
2. Frontend сохраняет профиль через `/profiles`.
3. Backend создает `trip_request` и фиксирует snapshot профиля.
4. Рекомендатель возвращает топ POI и сохраняет `recommendation_run`.
5. Route builder формирует маршрут с учетом стартовой и финальной точки.
6. Feedback и все промежуточные решения уходят в `decision_logs`.

## Компоненты развертывания

### Frontend

- Next.js App Router;
- запуск: `npm run dev`;
- production build: `npm run build`.

### Backend

- FastAPI + SQLAlchemy + Alembic;
- запуск API: `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000`;
- миграции: `uv run alembic upgrade head`.

### Database

- PostgreSQL в Docker через `compose.yaml`;
- опционально pgAdmin для визуальной проверки данных и decision log.

## Порядок внедрения

### Этап 1. Подготовка

- поднять PostgreSQL;
- выполнить миграции;
- убедиться, что каталог городов и POI загружен.

### Этап 2. Интеграция данных

- импортировать стартовый каталог;
- проверить категории `accommodation`, чтобы сценарий отеля работал в каждом демонстрационном городе;
- актуализировать media и source links.

### Этап 3. Демонстрационный запуск

- прогнать evaluation script;
- прогнать smoke-тесты;
- проверить построение маршрута с возвратом в отель;
- проверить запись feedback и decision log.

## Риски внедрения

- неполное покрытие accommodation в отдельных городах;
- зависимость от внешних open data API;
- возможные различия между seed-каталогом и production-наполнением;
- рост объема decision log при длительных экспериментах.

## Ожидаемый эффект

- сокращение времени на ручной выбор POI;
- повышение прозрачности рекомендаций;
- возможность воспроизводимо демонстрировать персонализированное планирование поездки;
- накопление decision log для последующих исследований качества СППР.
