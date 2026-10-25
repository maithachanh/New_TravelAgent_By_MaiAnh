from functools import lru_cache
from typing import Optional, Any
import time
import json

class SimpleCache:
    """Simple in-memory cache with TTL support"""
    def __init__(self):
        self._cache = {}
        self._ttl = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        if time.time() > self._ttl.get(key, 0):
            del self._cache[key]
            del self._ttl[key]
            return None
        return self._cache[key]

    def set(self, key: str, value: Any, ttl: int = 300):
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl

    def clear(self):
        self._cache.clear()
        self._ttl.clear()

# Global cache instance
cache = SimpleCache()

# Decorator for caching function results
def cached(ttl: int = 300):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{json.dumps(args, sort_keys=True)}_{json.dumps(kwargs, sort_keys=True)}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
