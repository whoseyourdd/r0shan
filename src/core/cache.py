from typing import Any, Dict, Optional
import time
from functools import lru_cache
from .constants import CACHE_TTL, MAX_CACHE_SIZE

class Cache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if time.time() - self._timestamps[key] < CACHE_TTL:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any):
        if len(self._cache) >= MAX_CACHE_SIZE:
            oldest_key = min(self._timestamps.items(), key=lambda x: x[1])[0]
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self):
        self._cache.clear()
        self._timestamps.clear()

# Global cache instance
game_cache = Cache()

# Decorator for caching expensive computations
def cached_result(ttl: int = CACHE_TTL):
    def decorator(func):
        @lru_cache(maxsize=MAX_CACHE_SIZE)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            result = game_cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                game_cache.set(cache_key, result)
            return result
        return wrapper
    return decorator