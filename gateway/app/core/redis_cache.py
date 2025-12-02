import os
import json
from typing import Any, Optional
import redis

_redis_client: Optional["redis.Redis"] = None

def get_redis() -> Optional["redis.Redis"]:
    """
    Lazy singleton Redis client.
    If REDIS_URL is not set or the redis library is not installed —
    returns None (the cache simply won't work).
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    if redis is None:
        return None

    url = os.getenv("REDIS_URL")
    if not url:
        return None

    _redis_client = redis.from_url(url, decode_responses = True)
    return _redis_client

def cache_get_json(key:str) -> Optional[dict]:
    r = get_redis()
    if r is None:
        return None
    try:
        raw = r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None

def cache_set_json(key:str, value:Any, ttl_seconds: int = 300) -> None:
    r = get_redis()
    if r is None:
        return None
    try:
        data = json.dumps(value)
        r.setex(key, ttl_seconds, data)
    except Exception:
        pass

def cache_delete(key:str) -> None:
    r = get_redis()
    if r is None:
        return None
    try:
        r.delete(key)
    except Exception:
        pass