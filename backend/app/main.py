from fastapi import FastAPI

from app.api.routes.health import router as health_router

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Service health and availability checks.",
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="TravelContext API",
        summary="API for the intelligent travel planning DSS prototype.",
        description=(
            "TravelContext API powers a prototype decision support system for "
            "personalized travel planning. The current API version exposes a "
            "health check and will be extended with cities, points of interest, "
            "recommendations, route planning, explanations, and feedback."
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
    return app


app = create_app()
