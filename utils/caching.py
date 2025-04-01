"""Caching utilities for ElevenTools."""

from typing import Any, Optional, Callable
import functools
import streamlit as st
import time
import json
import os
from datetime import datetime, timedelta


class Cache:
    """Simple cache implementation with TTL support."""

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache with TTL.

        Args:
            ttl_seconds: Time to live in seconds (default: 1 hour)
        """
        self.ttl = ttl_seconds
        self.cache_dir = os.path.join(os.path.dirname(__file__), "..", ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Use a hash of the key to avoid file system issues
        return os.path.join(self.cache_dir, f"{hash(key)}.json")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/missing
        """
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)

            # Check if expired
            if time.time() - data["timestamp"] > self.ttl:
                os.remove(cache_path)
                return None

            return data["value"]
        except Exception:
            return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(key)
        data = {"timestamp": time.time(), "value": value}

        with open(cache_path, "w") as f:
            json.dump(data, f)

    def clear(self) -> None:
        """Clear all cached data."""
        for file in os.listdir(self.cache_dir):
            if file.endswith(".json"):
                os.remove(os.path.join(self.cache_dir, file))


def cached(ttl_seconds: int = 3600) -> Callable:
    """Decorator for caching function results.

    Args:
        ttl_seconds: Cache TTL in seconds (default: 1 hour)

    Returns:
        Decorated function
    """
    cache = Cache(ttl_seconds)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        return wrapper

    return decorator


def st_cache(ttl_minutes: int = 60) -> Callable:
    """Streamlit-specific caching decorator with TTL.

    This combines Streamlit's caching with our TTL functionality.

    Args:
        ttl_minutes: Cache TTL in minutes (default: 60 minutes)

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        # Use Streamlit's cache
        @st.cache_data(ttl=timedelta(minutes=ttl_minutes))
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator
