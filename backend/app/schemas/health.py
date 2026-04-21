from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(
        examples=["ok"],
        description="Current backend service status.",
    )
