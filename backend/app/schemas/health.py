from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    app_name: str = Field(..., example="ScamShield AI")
    version: str = Field(..., example="1.0.0")
    environment: str = Field(..., example="development")
    database: str = Field(..., example="connected")
    timestamp: datetime = Field(..., example="2026-10-07T14:30:00Z")
