from typing import Any, Optional

from redis.asyncio import Redis

from app.core.config import settings
from app.domain.interfaces.cache_interface import ICache


class RedisCache(ICache):
    """Redis cache implementation."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        self.default_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return await self.redis.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        return await self.redis.set(key, value, ex=ttl or self.default_ttl)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        return bool(await self.redis.delete(key))

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(await self.redis.exists(key))

    async def clear(self) -> bool:
        """Clear all cache."""
        return bool(await self.redis.flushdb())

    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis.close()
