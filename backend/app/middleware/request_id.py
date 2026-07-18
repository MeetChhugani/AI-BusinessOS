import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars
from app.logging.config import logger

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check if X-Request-ID exists, otherwise generate a new UUID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Bind the context variables so any structlog log includes request_id
        bind_contextvars(request_id=request_id)

        request.state.request_id = request_id
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "request_failed",
                path=request.url.path,
                method=request.method,
                exception=str(e),
                duration_ms=duration_ms,
            )
            raise e

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "request_processed",
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response
