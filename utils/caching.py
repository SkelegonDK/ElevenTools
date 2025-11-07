"""Caching utilities for ElevenTools.

This module provides caching functionality with TTL (Time To Live) support for the ElevenTools application.
"""

from typing import Any, Optional, Callable
import functools
import streamlit as st
import time
import json
import os
from datetime import datetime, timedelta


class Cache:
    """Simple cache implementation with TTL support.

    This class provides a file-based caching system with automatic expiration of cached items.
    Cache files are stored in a .cache directory relative to this module.

    Attributes:
        ttl (int): Time to live in seconds for cached items.
        cache_dir (str): Directory path where cache files are stored.
    """

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache with TTL.

        Args:
            ttl_seconds (int): Time to live in seconds (default: 1 hour).
        """
        self.ttl = ttl_seconds
        self.cache_dir = os.path.join(os.path.dirname(__file__), "..", ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key.

        Args:
            key (str): Cache key to get path for.

        Returns:
            str: Absolute path to the cache file for the given key.
        """
        # Use a hash of the key to avoid file system issues
        return os.path.join(self.cache_dir, f"{hash(key)}.json")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired.

        Args:
            key (str): Cache key to retrieve.

        Returns:
            Optional[Any]: The cached value if found and not expired, None otherwise.
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
            key (str): Cache key to set.
            value (Any): Value to cache.
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

    def cleanup_expired(self) -> int:
        """Remove expired cache files.
        
        Returns:
            Number of expired files removed
        """
        removed_count = 0
        if not os.path.exists(self.cache_dir):
            return 0
        
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith(".json"):
                    cache_path = os.path.join(self.cache_dir, file)
                    try:
                        with open(cache_path, "r") as f:
                            data = json.load(f)
                        
                        # Check if expired
                        if time.time() - data["timestamp"] > self.ttl:
                            os.remove(cache_path)
                            removed_count += 1
                    except Exception:
                        # If file is corrupted or unreadable, remove it
                        try:
                            os.remove(cache_path)
                            removed_count += 1
                        except Exception:
                            pass  # Ignore errors during cleanup
        except Exception:
            pass  # Ignore errors during cleanup
        
        return removed_count


def cached(ttl_seconds: int = 3600) -> Callable:
    """Decorator for caching function results.

    This decorator provides a simple way to cache function results with a TTL.
    The cache key is generated from the function name and its arguments.

    Args:
        ttl_seconds (int): Cache TTL in seconds (default: 1 hour).

    Returns:
        Callable: A decorator function that adds caching to the decorated function.

    Example:
        @cached(ttl_seconds=3600)
        def expensive_function(arg1, arg2):
            # Function implementation
            return result
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
