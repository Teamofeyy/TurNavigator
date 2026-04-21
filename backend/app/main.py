from fastapi import FastAPI

from app.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="TravelContext API",
        description="Backend API for an intelligent travel planning DSS prototype.",
        version="0.1.0",
    )
    app.include_router(health_router)
    return app


app = create_app()
