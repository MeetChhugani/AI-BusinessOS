from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database.session import get_db_session
from app.logging.config import logger
from app.services.redis_service import redis_service

router = APIRouter(prefix="/health", tags=["System"])

@router.get("", summary="System health check endpoint")
async def check_health(db: AsyncSession = Depends(get_db_session)) -> dict:
    # 1. Database Health Check (SELECT 1)
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        logger.error("health_check_db_error", error=str(e))

    # 2. Redis Health Check (ping)
    redis_status = "healthy"
    try:
        ping_successful = await redis_service.ping()
        if not ping_successful:
            redis_status = "unhealthy"
    except Exception as e:
        redis_status = "unhealthy"
        logger.error("health_check_redis_error", error=str(e))

    overall_status = "healthy"
    if db_status == "unhealthy" or redis_status == "unhealthy":
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "services": {
            "api": "healthy",
            "database": db_status,
            "redis": redis_status,
        },
    }
