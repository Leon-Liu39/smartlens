"""
Async Redis helper — connection pool, JSON cache, pub/sub publish.
"""
import json, asyncio
from typing import Any, Optional
import redis.asyncio as aioredis
from config import settings

_pool: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    global _pool
    if _pool is None:
        _pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _pool

async def cache_get(key: str) -> Optional[Any]:
    r = await get_redis()
    raw = await r.get(key)
    return json.loads(raw) if raw else None

async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value))

async def publish(channel: str, payload: dict) -> None:
    r = await get_redis()
    await r.publish(channel, json.dumps(payload))

async def subscribe(channel: str):
    """Async generator — yields messages from a Redis pub/sub channel."""
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg.get("data"):
                yield msg["data"]
            else:
                await asyncio.sleep(0.05)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
