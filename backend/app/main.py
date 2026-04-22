from fastapi import FastAPI

from app.api.routes.cities import router as cities_router
from app.api.routes.health import router as health_router
from app.api.routes.planning import router as planning_router
from app.api.routes.pois import router as pois_router
from app.api.routes.routes import router as routes_router

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Service health and availability checks.",
    },
    {
        "name": "cities",
        "description": "Cities available for travel planning in the MVP dataset.",
    },
    {
        "name": "points-of-interest",
        "description": "Tourism, food, accommodation, shopping, and entertainment objects.",
    },
    {
        "name": "planning",
        "description": "Trip requests and personalized recommendation generation.",
    },
    {
        "name": "routes",
        "description": "Route building and route plan retrieval.",
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="TravelContext API",
        summary="API for the intelligent travel planning DSS prototype.",
        description=(
            "TravelContext API powers a prototype decision support system for "
            "personalized travel planning. The current API version exposes "
            "health checks, cities, points of interest, trip requests, and "
            "personalized recommendations from seed data. It will be extended "
            "with feedback and persistent storage."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=OPENAPI_TAGS,
        contact={
            "name": "TravelContext project",
        },
        license_info={
            "name": "Academic prototype",
        },
        servers=[
            {
                "url": "http://127.0.0.1:8000",
                "description": "Local development server",
            },
        ],
    )
    app.include_router(health_router)
    app.include_router(cities_router)
    app.include_router(pois_router)
    app.include_router(planning_router)
    app.include_router(routes_router)
    return app


app = create_app()
