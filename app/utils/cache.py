import os

from aiocache import SimpleMemoryCache

CACHE_TTL = int(os.getenv("USER_CACHE_TTL", 300))  # default 5 menit

# Singleton memory cache instance
cache = SimpleMemoryCache()


def user_cache_key(user_id: str) -> str:
    return f"user:{user_id}"


async def get_user_cache(user_id: str):
    return await cache.get(user_cache_key(user_id))


async def set_user_cache(user_id: str, user_data: dict, ttl: int = CACHE_TTL):
    await cache.set(user_cache_key(user_id), user_data, ttl=ttl)


async def delete_user_cache(user_id: str):
    await cache.delete(user_cache_key(user_id))
