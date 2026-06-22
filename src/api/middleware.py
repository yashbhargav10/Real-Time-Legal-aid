import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger("api.middleware")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"{request.client.host} - \"{request.method} {request.url.path}\" "
                f"{response.status_code} - {process_time:.4f}s"
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Unhandled Exception: {request.client.host} - \"{request.method} {request.url.path}\" "
                f"500 - {process_time:.4f}s - Error: {e}"
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )
