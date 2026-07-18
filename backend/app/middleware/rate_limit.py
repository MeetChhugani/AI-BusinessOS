from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.exceptions.custom_exceptions import RateLimitException
from app.logging.config import logger
from app.services.redis_service import redis_service

class RateLimiter:
    @staticmethod
    async def is_rate_limited(key: str, limit: int, window_seconds: int) -> bool:
        """Checks rate limit using fixed-window counter with Redis."""
        try:
            redis_key = f"ratelimit:{key}"
            client = await redis_service._get_client()

            current = await client.get(redis_key)
            if current is not None and int(current) >= limit:
                return True

            # Use a pipeline to increment and set expiration atomically
            async with client.pipeline(transaction=True) as pipe:
                await pipe.incr(redis_key)
                if current is None:
                    await pipe.expire(redis_key, window_seconds)
                await pipe.execute()

            return False
        except Exception as e:
            logger.error("rate_limiter_redis_error", key=key, error=str(e))
            # Fail open in production for database safety, but report warning
            return False

class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Any:
        path = request.url.path
        # Bypass rate limits for docs and health
        if (
            path.startswith("/docs")
            or path.startswith("/openapi.json")
            or path.startswith("/redoc")
            or path.startswith("/api/v1/health")
        ):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"global:{client_ip}"

        # Limit: 100 requests per 60 seconds
        if await RateLimiter.is_rate_limited(key, limit=100, window_seconds=60):
            logger.warning("global_rate_limit_triggered", ip=client_ip, path=path)
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RateLimitException",
                        "message": "Global rate limit exceeded (100 req/min). Please slow down.",
                        "details": None,
                    },
                },
            )

        return await call_next(request)

# Route-specific dependencies
async def check_login_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"login:{client_ip}"
    # Limit: 10 attempts per 3600 seconds (1 hour)
    if await RateLimiter.is_rate_limited(key, limit=10, window_seconds=3600):
        logger.warning("login_rate_limit_triggered", ip=client_ip)
        raise RateLimitException("Too many login attempts. Please try again in an hour.")

async def check_password_reset_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"pw_reset:{client_ip}"
    # Limit: 5 attempts per 3600 seconds (1 hour)
    if await RateLimiter.is_rate_limited(key, limit=5, window_seconds=3600):
        logger.warning("password_reset_rate_limit_triggered", ip=client_ip)
        raise RateLimitException("Too many password reset requests. Please try again in an hour.")

from typing import Any
from fastapi.responses import JSONResponse
