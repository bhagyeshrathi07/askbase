"""Dependency checks used by the /health endpoint.

Each check answers one question (can the app reach this service?) and
returns a bool. The endpoint treats an exception as "down".
"""

from collections.abc import Awaitable, Callable

import redis.asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

HealthCheck = Callable[[], Awaitable[bool]]


def postgres_check(database_url: str) -> HealthCheck:
    engine = create_async_engine(database_url, pool_pre_ping=True)

    async def check() -> bool:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1

    return check


def redis_check(redis_url: str) -> HealthCheck:
    client = aioredis.from_url(redis_url)

    async def check() -> bool:
        return bool(await client.ping())

    return check
