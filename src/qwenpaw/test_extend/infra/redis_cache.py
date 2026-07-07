# -*- coding: utf-8 -*-
"""Redis cache configuration for the test platform.

When Redis is available (TEST_PLATFORM_REDIS_URL is set), all cache
operations go through Redis. Otherwise an in-memory LRU dict is used.

Provides:
  - redis_available() -> bool
  - get_redis() -> redis.Redis | None
  - cache_get / cache_set / cache_delete / cache_clear helpers
  - MemoryCache fallback with same interface
"""

import asyncio
import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

_redis_client: Optional[Any] = None  # redis.asyncio.Redis
_memory_cache: Optional[Any] = None  # MemoryCache fallback


class MemoryCache:
    """Thread-safe LRU dict fallback when Redis is unavailable."""

    def __init__(self, maxsize: int = 2048):
        from collections import OrderedDict
        self._store: OrderedDict = OrderedDict()
        self._maxsize = maxsize
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
                return self._store[key]
            return None

    async def set(self, key: str, value: str, ttl: int = 0) -> None:
        async with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = value
            while len(self._store) > self._maxsize:
                self._store.popitem(last=False)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    async def exists(self, key: str) -> bool:
        async with self._lock:
            return key in self._store


async def init_redis():
    """Initialize the Redis client.

    Reads TEST_PLATFORM_REDIS_URL from env; falls back to memory cache.
    """
    global _redis_client, _memory_cache
    redis_url = os.getenv("TEST_PLATFORM_REDIS_URL", "")

    if redis_url:
        try:
            import redis.asyncio as aioredis
            _redis_client = aioredis.from_url(
                redis_url,
                max_connections=20,
                decode_responses=True,
            )
            await _redis_client.ping()
            logger.info("Redis connected: %s", _redis_url)
        except Exception as e:
            logger.warning("Redis connection failed (%s), falling back to memory cache", e)
            _redis_client = None

    if _redis_client is None:
        _memory_cache = MemoryCache()
        logger.info("Using in-memory cache (Redis unavailable)")


async def close_redis():
    """Close the Redis connection."""
    global _redis_client, _memory_cache
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


def redis_available() -> bool:
    return _redis_client is not None


async def cache_get(key: str) -> Optional[str]:
    if _redis_client:
        return await _redis_client.get(key)
    return await _memory_cache.get(key)


async def cache_set(key: str, value: str, ttl: int = 3600) -> None:
    if _redis_client:
        await _redis_client.set(key, value, ex=ttl)
    else:
        await _memory_cache.set(key, value, ttl)


async def cache_delete(key: str) -> None:
    if _redis_client:
        await _redis_client.delete(key)
    else:
        await _memory_cache.delete(key)


async def cache_clear() -> None:
    if _redis_client:
        await _redis_client.flushdb()
    else:
        await _memory_cache.clear()


async def cache_get_json(key: str) -> Optional[dict]:
    raw = await cache_get(key)
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None


async def cache_set_json(key: str, data: dict, ttl: int = 3600) -> None:
    await cache_set(key, json.dumps(data, ensure_ascii=False, default=str), ttl)


class cached:
    """Async decorator that caches function results in Redis/memory.

    Usage:
        @cached(ttl=600, key_prefix="iteration")
        async def get_iteration(iteration_id: str) -> dict:
            ...
    """

    def __init__(self, ttl: int = 3600, key_prefix: str = ""):
        self.ttl = ttl
        self.key_prefix = key_prefix

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            suffix = ":".join(str(a) for a in args)
            if kwargs:
                suffix += ":" + ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"test:{self.key_prefix}:{func.__name__}:{suffix}" if self.key_prefix else f"test:{func.__name__}:{suffix}"
            cached_value = await cache_get(cache_key)
            if cached_value is not None:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    pass
                return cached_value
            result = await func(*args, **kwargs)
            if result is not None:
                serialized = json.dumps(result, ensure_ascii=False, default=str)
                await cache_set(cache_key, serialized, self.ttl)
            return result

        wrapper.__name__ = func.__name__
        wrapper.__qualname__ = func.__qualname__
        return wrapper
