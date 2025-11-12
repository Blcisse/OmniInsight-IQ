from __future__ import annotations

from collections import OrderedDict
from typing import Any, Optional, Tuple


_CACHE_CAPACITY = 5
_MODEL_CACHE: "OrderedDict[Tuple[str, Optional[str]], Any]" = OrderedDict()


def initialize_model_cache(capacity: int = 5) -> None:
    """Initialize/reset the in-memory model cache with a maximum capacity."""
    global _CACHE_CAPACITY, _MODEL_CACHE
    _CACHE_CAPACITY = max(1, int(capacity))
    _MODEL_CACHE = OrderedDict()


def _cache_key(model_name: str, version: Optional[str]) -> Tuple[str, Optional[str]]:
    return (model_name, version)


def store_model_in_memory(model_name: str, model: Any, *, version: Optional[str] = None) -> None:
    """Store a model in the LRU cache; evicts the least-recently-used when full."""
    key = _cache_key(model_name, version)
    if key in _MODEL_CACHE:
        _MODEL_CACHE.move_to_end(key)
    _MODEL_CACHE[key] = model
    # Evict
    while len(_MODEL_CACHE) > _CACHE_CAPACITY:
        _MODEL_CACHE.popitem(last=False)


def retrieve_cached_model(model_name: str, *, version: Optional[str] = None) -> Optional[Any]:
    key = _cache_key(model_name, version)
    model = _MODEL_CACHE.get(key)
    if model is not None:
        _MODEL_CACHE.move_to_end(key)
    return model

