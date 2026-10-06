from httpx import ASGITransport, AsyncClient

from app.main import create_app


async def _get_health(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/health")


async def test_health_ok_when_all_dependencies_reachable():
    async def db_ok() -> bool:
        return True

    async def redis_ok() -> bool:
        return True

    app = create_app(check_postgres=db_ok, check_redis=redis_ok)
    resp = await _get_health(app)

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "postgres": True, "redis": True}


async def test_health_degraded_when_a_dependency_is_down():
    async def db_ok() -> bool:
        return True

    async def redis_down() -> bool:
        return False

    app = create_app(check_postgres=db_ok, check_redis=redis_down)
    resp = await _get_health(app)

    assert resp.status_code == 503
    assert resp.json() == {"status": "degraded", "postgres": True, "redis": False}


async def test_health_treats_a_raising_check_as_down():
    async def db_ok() -> bool:
        return True

    async def redis_raises() -> bool:
        raise ConnectionError("redis unreachable")

    app = create_app(check_postgres=db_ok, check_redis=redis_raises)
    resp = await _get_health(app)

    assert resp.status_code == 503
    assert resp.json()["redis"] is False


def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@db:5432/askbase")
    monkeypatch.setenv("REDIS_URL", "redis://cache:6379/1")

    from app.config import Settings

    s = Settings()
    assert s.database_url == "postgresql+asyncpg://u:p@db:5432/askbase"
    assert s.redis_url == "redis://cache:6379/1"
