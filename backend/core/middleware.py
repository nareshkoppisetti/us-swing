"""
File path: backend/core/middleware.py
Purpose: FastAPI middleware stack — request logging, rate limiting, global exception handler.
         Call setup_middleware(app) once from main.py.

SPEC Reference: Section 9.1, 17.3
BUILD_PLAN Reference: Phase 1.2

Rate limits (SPEC Section 17.3):
  /api/v1/auth/login           → 5  req/min per IP
  /api/v1/symbols/search       → 30 req/min per user
  /api/v1/predictions/generate → 10 req/min per user
  /api/v1/admin/*              → 60 req/min per user
  All others                   → 120 req/min per user

Standard error envelope:
  {"success": false, "error": {"code": "...", "message": "...", "details": {}},
   "meta": {"request_id": "uuid", "timestamp": "ISO8601"}}
"""

import time
import uuid
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.exceptions import AppException, RateLimitError

logger = logging.getLogger("app")


def _exception_to_response(exc: Exception, request_id: str | None) -> JSONResponse:
    """
    Convert any exception to the standard JSON error envelope.
    Shared by both middleware dispatch() methods AND global_exception_handler,
    so behavior is identical whichever layer catches it.
    """
    if isinstance(exc, AppException):
        logger.warning(
            "app_exception: %s", exc.message,
            extra={"request_id": request_id, "code": exc.code, "status": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.to_dict(),
                "meta": {"request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()},
            },
        )
    logger.exception("unhandled_exception", exc_info=exc, extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "details": {}},
            "meta": {"request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()},
        },
    )


# ── Rate limit configuration ──────────────────────────────────────────────────

RATE_LIMIT_RULES: list[tuple[str, int]] = [
    # (path_prefix, requests_per_minute)
    # More-specific rules must come FIRST
    ("/api/v1/auth/login",           5),
    ("/api/v1/symbols/search",       30),
    ("/api/v1/predictions/generate", 10),
    ("/api/v1/admin/",               60),
]
DEFAULT_RATE_LIMIT = 120  # req/min for all other endpoints


def _get_rate_limit(path: str) -> int:
    """Return the req/min limit for the given path."""
    for prefix, limit in RATE_LIMIT_RULES:
        if path.startswith(prefix):
            return limit
    return DEFAULT_RATE_LIMIT


def _rate_limit_key(request: Request, path: str) -> str:
    """
    Build a diskcache key for rate limiting.
    Uses user_id from JWT if available, else client IP.
    Key format: ratelimit:{identifier}:{path_bucket}:{minute_window}
    """
    # Try to get user_id from request state (set by auth dependency)
    user_id = getattr(request.state, "user_id", None)
    identifier = user_id or (request.client.host if request.client else "unknown")
    # Use 1-minute windows (Unix timestamp // 60)
    window = int(time.time()) // 60
    # Bucket the path to the matching rule prefix (or "default")
    bucket = "default"
    for prefix, _ in RATE_LIMIT_RULES:
        if path.startswith(prefix):
            bucket = prefix.replace("/", "_").strip("_")
            break
    return f"ratelimit:{identifier}:{bucket}:{window}"


# ── Request Logging Middleware ────────────────────────────────────────────────

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every request with:
      - request_id (UUID4, attached to request.state and X-Request-ID response header)
      - method, path, status_code, duration_ms, client_ip
    Structured as JSON via python-json-logger.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            # BaseHTTPMiddleware (especially stacked, as here) can turn an
            # exception raised deep in dependency resolution — e.g.
            # AuthenticationError from get_current_user — into an unhandled
            # ExceptionGroup instead of letting FastAPI's registered
            # exception handler convert it to a clean JSON response. Catch
            # and convert it here directly so that never happens.
            response = _exception_to_response(exc, request_id)

        duration_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )
        return response


# ── Rate Limiting Middleware ──────────────────────────────────────────────────

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-user (or per-IP) sliding-window rate limiter using diskcache.
    Increments a counter keyed by (identifier, path_bucket, minute_window).
    Returns HTTP 429 with Retry-After header on limit exceeded.
    """

    def __init__(self, app, cache=None):
        super().__init__(app)
        self._cache = cache  # diskcache.Cache instance, injected at startup

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = getattr(request.state, "request_id", None)

        # Skip rate limiting if cache not initialized yet (startup) or for health checks
        if self._cache is None or request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            try:
                return await call_next(request)
            except Exception as exc:
                return _exception_to_response(exc, request_id)

        path = request.url.path
        limit = _get_rate_limit(path)
        key = _rate_limit_key(request, path)

        try:
            count = self._cache.get(key, default=0)
            if count >= limit:
                logger.warning(
                    "rate_limit_exceeded",
                    extra={"path": path, "limit": limit, "key": key},
                )
                return _error_response(
                    status_code=429,
                    code="RATE_LIMIT_EXCEEDED",
                    message=f"Too many requests. Limit: {limit}/min. Please slow down.",
                    request_id=getattr(request.state, "request_id", None),
                    extra_headers={"Retry-After": "60"},
                )
            # Increment with 70-second TTL (covers the full 60s window + buffer)
            self._cache.set(key, count + 1, expire=70)
        except Exception as e:
            # Never let cache errors block requests — log and continue
            logger.error("rate_limit_cache_error", extra={"error": str(e)})

        try:
            return await call_next(request)
        except Exception as exc:
            return _exception_to_response(exc, request_id)


# ── Global Exception Handler ──────────────────────────────────────────────────

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches unhandled exceptions that reach FastAPI's own exception middleware
    (i.e. anything that wasn't already caught by the RequestLoggingMiddleware /
    RateLimitMiddleware try/except wrappers above). Delegates to the same
    conversion logic so behavior is identical either way.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return _exception_to_response(exc, request_id)


# ── Standard success response helper ─────────────────────────────────────────

def success_response(data: dict | list, request_id: str | None = None) -> dict:
    """
    Wrap any response data in the standard success envelope.
    Usage in routers: return success_response({"user": user_dict}, request_id)
    """
    return {
        "success": True,
        "data": data,
        "meta": {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


def _error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: str | None,
    details: dict | None = None,
    extra_headers: dict | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {"code": code, "message": message, "details": details or {}},
            "meta": {
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        },
        headers=extra_headers or {},
    )


# ── Setup function called from main.py ───────────────────────────────────────

def setup_middleware(app: FastAPI, cache=None) -> None:
    """
    Register all middleware and exception handlers on the FastAPI app.
    Called once in main.py before the app starts.

    Args:
        app:   The FastAPI application instance
        cache: diskcache.Cache instance for rate limiting (optional at startup)
    """
    # Order matters: added last = runs first
    app.add_middleware(RateLimitMiddleware, cache=cache)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_exception_handler(Exception, global_exception_handler)
    logger.info("Middleware registered: RequestLogging, RateLimit, GlobalExceptionHandler")