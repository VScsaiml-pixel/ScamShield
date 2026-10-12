from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def check_health(db: Session = Depends(get_db)):
    """
    Health check endpoint that verifies the FastAPI backend and SQLite database connectivity.
    """
    db_status = "connected"
    try:
        # Verify database connection with a lightweight check
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        app_name=settings.APP_NAME,
        version="1.0.0",
        environment=settings.APP_ENV,
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )
