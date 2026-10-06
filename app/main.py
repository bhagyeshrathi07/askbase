"""FastAPI application factory."""

import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.health import HealthCheck, postgres_check, redis_check


def create_app(
    check_postgres: HealthCheck | None = None,
    check_redis: HealthCheck | None = None,
) -> FastAPI:
    """Build the app. Checks are injectable so tests need no running services."""
    settings = get_settings()
    check_postgres = check_postgres or postgres_check(settings.database_url)
    check_redis = check_redis or redis_check(settings.redis_url)

    app = FastAPI(title=settings.app_name, version="0.1.0")

    async def _safe(check: HealthCheck) -> bool:
        try:
            return bool(await asyncio.wait_for(check(), timeout=2.0))
        except Exception:  # noqa: BLE001 - a health check must report, never crash
            return False

    @app.get("/health", tags=["ops"])
    async def health() -> JSONResponse:
        postgres_ok, redis_ok = await asyncio.gather(_safe(check_postgres), _safe(check_redis))
        healthy = postgres_ok and redis_ok
        body = {
            "status": "ok" if healthy else "degraded",
            "postgres": postgres_ok,
            "redis": redis_ok,
        }
        return JSONResponse(body, status_code=200 if healthy else 503)

    return app


app = create_app()
