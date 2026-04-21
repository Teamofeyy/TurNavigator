# Intelligent Travel Planning DSS Prototype

## 1. Назначение проекта

Проект представляет собой прототип интеллектуальной информационной системы поддержки планирования путешествий. Система помогает пользователю подобрать маршрут по городу с учетом интересов, бюджета, времени, темпа перемещения и других ограничений.

Основная идея прототипа: пользователь задает контекст поездки, система получает данные о городе и точках интереса, ранжирует объекты, собирает маршрут и объясняет, почему предложены именно эти рекомендации.

## 2. Результат разработки

В результате разработки должны быть подготовлены:

- веб-приложение с пользовательским интерфейсом;
- backend API для работы с городами, профилем пользователя, рекомендациями и маршрутами;
- база данных с городами, точками интереса, профилями и журналом решений;
- модуль загрузки и нормализации открытых геоданных;
- модуль персонализированного ранжирования объектов;
- модуль объяснения рекомендаций;
- документация по архитектуре, стеку, данным, API и запуску;
- GitHub-репозиторий с исходным кодом;
- деплой приложения на хостинг.

## 3. Технологический стек

### Frontend

- Next.js;
- TypeScript;
- Tailwind CSS;
- MapLibre GL JS или Leaflet для карты;
- fetch/axios для обращения к backend API.

### Backend

- Python;
- FastAPI;
- Pydantic для схем запросов и ответов;
- SQLAlchemy или SQLModel для работы с базой данных;
- Alembic для миграций.

### База данных

- PostgreSQL;
- SQLite допускается только на самом раннем этапе локального прототипа;
- в перспективе может использоваться pgvector для семантического поиска и похожих объектов.

### Источники данных

- OpenStreetMap / Overpass API для городских объектов;
- OpenTripMap для туристических объектов;
- Wikidata и Wikipedia для описаний, ссылок и дополнительной информации;
- GeoNames или Wikidata для стартового списка городов;
- OSRM или OpenRouteService для маршрутов и расстояний.

## 4. Архитектура системы

Система делится на следующие модули:

- frontend application;
- backend API;
- database;
- data ingestion module;
- recommendation engine;
- route builder;
- explanation module;
- decision log module.

Общий поток работы:

1. Пользователь выбирает город, интересы, бюджет, даты и темп поездки.
2. Backend проверяет, есть ли данные по городу в локальной базе.
3. Если данных нет или они устарели, запускается загрузка из внешних источников.
4. Точки интереса нормализуются к единой модели категорий.
5. Рекомендатель рассчитывает оценку каждого объекта.
6. Route builder формирует маршрут с учетом времени, расстояний и бюджета.
7. Explanation module формирует объяснение результата.
8. Decision log сохраняет запрос, рекомендации и обратную связь пользователя.

## 5. Модель данных

### City

- id;
- name;
- region;
- country;
- latitude;
- longitude;
- population;
- source;
- external_id;
- wikidata_id;
- osm_id.

### PointOfInterest

- id;
- city_id;
- name;
- category;
- subcategory;
- latitude;
- longitude;
- address;
- description;
- opening_hours;
- website;
- phone;
- source;
- external_id;
- wikidata_id;
- osm_tags;
- estimated_price_level;
- popularity_score;
- data_quality_score.

### UserProfile

- id;
- interests;
- budget_level;
- max_budget;
- pace;
- max_walking_distance_km;
- preferred_transport;
- accessibility_needs;
- explanation_level.

### TripRequest

- id;
- user_profile_id;
- city_id;
- start_date;
- end_date;
- days_count;
- daily_time_limit_hours;
- budget;
- selected_interests;
- constraints.

### Recommendation

- id;
- trip_request_id;
- poi_id;
- score;
- rank;
- matched_interests;
- constraint_status;
- explanation.

### RoutePlan

- id;
- trip_request_id;
- total_distance_km;
- total_time_minutes;
- estimated_budget;
- route_points;
- explanation_summary.

### DecisionLog

- id;
- user_profile_id;
- trip_request_id;
- input_context;
- generated_recommendations;
- user_feedback;
- created_at.

## 6. API

### Health

- `GET /health` - проверка работоспособности backend. Endpoint задокументирован в OpenAPI и доступен в Swagger UI.

Автоматически генерируемая документация:

- Swagger UI: `http://127.0.0.1:8000/docs`;
- ReDoc: `http://127.0.0.1:8000/redoc`;
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`;
- экспортированная схема: `docs/openapi.json`.

### Cities

- `GET /cities` - список доступных городов, реализовано на seed-данных;
- `GET /cities/{city_id}` - информация о городе, реализовано на seed-данных;
- `POST /cities/import` - импорт стартового набора городов.

### Points of Interest

- `GET /cities/{city_id}/pois` - список POI по городу, реализовано на seed-данных;
- `POST /cities/{city_id}/pois/import` - загрузка POI из внешних источников;
- `GET /pois/{poi_id}` - карточка конкретного объекта, реализовано на seed-данных.

### Profile

- `POST /profiles` - создание профиля пользователя;
- `GET /profiles/{profile_id}` - получение профиля;
- `PATCH /profiles/{profile_id}` - изменение профиля.

### Planning

- `POST /trip-requests` - создание запроса на планирование поездки;
- `POST /recommendations/generate` - генерация рекомендаций;
- `POST /routes/build` - построение маршрута;
- `GET /routes/{route_id}` - получение маршрута.

### Feedback

- `POST /feedback` - сохранение оценки пользователя;
- `GET /decision-logs` - журнал решений.

## 7. Алгоритм рекомендаций

Базовая формула ранжирования:

```text
score =
  0.35 * interest_match +
  0.20 * budget_match +
  0.15 * route_convenience +
  0.15 * pace_match +
  0.10 * popularity_score +
  0.05 * data_quality_score
```

Каждая рекомендация должна сопровождаться объяснением:

- какие интересы пользователя совпали с объектом;
- какие ограничения соблюдены;
- почему объект попал в маршрут;
- какие компромиссы были сделаны.

## 8. Работа с данными

На первом этапе система работает не со всеми городами России, а с ограниченным стартовым набором городов. Это позволяет сфокусироваться на методе персонализации, а не на создании аналога 2GIS.

Стартовый набор городов:

- Москва;
- Санкт-Петербург;
- Казань;
- Нижний Новгород;
- Екатеринбург;
- Ростов-на-Дону.

Для каждого города загружаются:

- достопримечательности;
- музеи;
- парки;
- театры;
- кафе и рестораны;
- гостиницы;
- магазины первой необходимости.

В первой версии проекта добавлены seed-файлы:

- `backend/app/seeds/cities.json`;
- `backend/app/seeds/pois.json`.

Seed-данные используются для быстрого запуска MVP без зависимости от внешних API. Источник таких записей помечается как `manual_seed`. В следующих версиях эти данные можно заменить или дополнить импортом из OpenStreetMap, OpenTripMap, Wikidata и Wikipedia.

Категории внешних источников приводятся к внутренней таксономии:

- culture;
- history;
- nature;
- food;
- accommodation;
- shopping;
- entertainment;
- transport;
- service.

## 9. План разработки

### Этап 1. Каркас проекта

- создать репозиторий;
- создать структуру frontend/backend/docs;
- поднять FastAPI;
- поднять Next.js;
- добавить базовую документацию запуска.

### Этап 2. База и модели

- описать модели City, PointOfInterest, UserProfile, TripRequest, Recommendation, RoutePlan, DecisionLog;
- подключить PostgreSQL или временно SQLite;
- добавить миграции;
- создать seed-данные.

### Этап 3. Загрузка данных

- реализовать импорт списка городов;
- реализовать загрузку POI из OpenStreetMap или OpenTripMap;
- сохранить нормализованные данные в базе;
- добавить проверку качества данных.

### Этап 4. Рекомендатель

- реализовать расчет score;
- добавить фильтрацию по ограничениям;
- добавить объяснения рекомендаций;
- сохранить результат в журнал решений.

### Этап 5. Маршрут

- собрать выбранные POI в дневной маршрут;
- посчитать примерное расстояние и время;
- вывести маршрут на карте.

### Этап 6. Интерфейс

- форма планирования;
- карточки рекомендаций;
- карта;
- экран результата;
- оценка маршрута пользователем.

### Этап 7. Подготовка к сдаче

- скриншоты;
- README;
- итоговый документ по реализации;
- публикация кода на GitHub;
- подготовка к деплою.

## 10. Хостинг

Предварительный вариант деплоя:

- frontend: Vercel;
- backend: Render или Railway;
- database: Supabase PostgreSQL или Railway PostgreSQL.

Финальный выбор хостинга нужно подтвердить ближе к июню 2026 года с учетом актуальных тарифов и ограничений бесплатных планов.

## 11. Скриншоты для отчета

Нужно подготовить:

- главная страница / форма планирования;
- выбор интересов и ограничений;
- список рекомендаций;
- карта с маршрутом;
- карточка объяснения рекомендации;
- журнал решений или экран обратной связи;
- Swagger/OpenAPI backend;
- структура GitHub-репозитория.

## 12. Инструкция запуска

Backend уже инициализирован как FastAPI-приложение с управлением зависимостями через uv.

### Backend

```bash
cd backend
UV_CACHE_DIR=../.uv-cache uv run uvicorn app.main:app --reload
```

Проверка:

```bash
curl http://127.0.0.1:8000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 13. Ссылки

Этот раздел заполняется после реализации.

- GitHub repository:
- Local frontend URL:
- Local backend URL: http://127.0.0.1:8000
- Production frontend URL:
- Production backend URL:
