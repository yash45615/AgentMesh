from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.core.redis import redis_client
from app.db.database import SessionLocal


async def test_database():

    print()
    print("[CHAOS] Testing database connectivity...")

    db = SessionLocal()

    try:

        result = db.execute(
            text("SELECT 1")
        )

        value = result.scalar()

        if value != 1:

            raise RuntimeError(
                "Unexpected database response."
            )

        print(
            "[PASS] Database is reachable."
        )

    finally:

        db.close()


async def test_redis():

    print()
    print("[CHAOS] Testing Redis connectivity...")

    result = await redis_client.ping()

    if not result:

        raise RuntimeError(
            "Redis ping failed."
        )

    print(
        "[PASS] Redis is reachable."
    )


async def test_redis_write_read():

    print()
    print(
        "[CHAOS] Testing Redis "
        "write/read recovery path..."
    )

    key = (
        "agentmesh:chaos:test"
    )

    await redis_client.set(
        key,
        "chaos-ok",
        ex=30,
    )

    value = await redis_client.get(
        key
    )

    if value != "chaos-ok":

        raise RuntimeError(
            "Redis write/read validation failed."
        )

    await redis_client.delete(key)

    print(
        "[PASS] Redis write/read works."
    )


async def main():

    print("=" * 70)
    print("AgentMesh Dependency Chaos Checks")
    print("=" * 70)

    await test_database()

    await test_redis()

    await test_redis_write_read()

    print()
    print(
        "Dependency chaos checks completed."
    )


if __name__ == "__main__":

    asyncio.run(main())