import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_token
from app.database.session import SessionLocal
from app.models.chat import ActivityLog


class ActivityLoggingMiddleware(BaseHTTPMiddleware):
    """Logs each API call for the Admin Dashboard's activity feed / API usage analytics."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 1)

        if request.url.path.startswith("/api/v1") and request.url.path not in ("/api/v1/auth/login",):
            try:
                user_id = None
                auth_header = request.headers.get("authorization", "")
                if auth_header.startswith("Bearer "):
                    payload = decode_token(auth_header.split(" ", 1)[1])
                    if payload:
                        user_id = payload.get("sub")

                db = SessionLocal()
                db.add(ActivityLog(
                    user_id=user_id,
                    action=f"{request.method} {request.url.path}",
                    endpoint=request.url.path,
                    status_code=str(response.status_code),
                    meta={"duration_ms": duration_ms},
                    ip_address=request.client.host if request.client else None,
                ))
                db.commit()
                db.close()
            except Exception:
                pass  # never let logging break the request

        return response
