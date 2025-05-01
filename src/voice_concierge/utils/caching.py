# src/voice_concierge/utils/caching.py
import json
import os
import hashlib
from typing import Any, Optional, Callable
import functools
import time

from voice_concierge.utils.logging_utils import get_logger
from voice_concierge.config import settings

logger = get_logger(__name__)


def get_cache_dir() -> str:
    """Get the cache directory, creating it if necessary."""
    cache_dir = os.path.join(os.path.dirname(settings.log_file), "cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir


def compute_hash(*args, **kwargs) -> str:
    """Compute a hash for the given arguments."""
    content = json.dumps((args, kwargs), sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


def cache_result(ttl: Optional[int] = None) -> Callable:
    """Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds. If None, cache never expires.

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Skip caching if explicitly disabled
            if kwargs.get("skip_cache", False):
                if "skip_cache" in kwargs:
                    del kwargs["skip_cache"]
                return func(*args, **kwargs)

            # Compute cache key
            cache_key = compute_hash(func.__name__, *args, **kwargs)
            cache_file = os.path.join(get_cache_dir(), f"{cache_key}.json")

            # Check if cache exists and is valid
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r") as f:
                        cached_data = json.load(f)

                    # Check if cache has expired
                    if ttl is not None:
                        timestamp = cached_data.get("timestamp", 0)
                        if time.time() - timestamp > ttl:
                            logger.debug(f"Cache expired for {func.__name__}")
                        else:
                            logger.debug(f"Cache hit for {func.__name__}")
                            return cached_data["result"]
                    else:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return cached_data["result"]
                except Exception as e:
                    logger.warning(f"Error reading cache: {str(e)}")

            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)

            try:
                with open(cache_file, "w") as f:
                    json.dump({"timestamp": time.time(), "result": result}, f)
            except Exception as e:
                logger.warning(f"Error writing cache: {str(e)}")

            return result

        return wrapper

    return decorator
