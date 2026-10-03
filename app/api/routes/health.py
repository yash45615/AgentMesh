from fastapi import APIRouter
from sqlalchemy import text

from app.core.redis import redis_client
from app.db.database import SessionLocal
from app.observability.metrics import metrics


router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "AgentMesh",
    }


@router.get("/health/database")
def database_health():

    db = SessionLocal()

    try:

        db.execute(
            text("SELECT 1")
        )

        return {
            "status": "healthy",
            "database": "postgresql",
        }

    except Exception as exc:

        return {
            "status": "unhealthy",
            "database": "postgresql",
            "error": str(exc),
        }

    finally:

        db.close()


@router.get("/health/redis")
async def redis_health():

    try:

        result = await redis_client.ping()

        return {
            "status": (
                "healthy"
                if result
                else "unhealthy"
            ),
            "redis": "available",
        }

    except Exception as exc:

        return {
            "status": "unhealthy",
            "redis": "unavailable",
            "error": str(exc),
        }


@router.get("/metrics")
def get_metrics():

    return metrics.snapshot()