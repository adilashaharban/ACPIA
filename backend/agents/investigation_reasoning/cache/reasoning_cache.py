# -*- coding: utf-8 -*-
"""Reasoning package response cache."""

import time
from typing import Dict, Optional, Tuple
from backend.agents.investigation_reasoning.schema import ReasoningPackage

class ReasoningCache:
    """Stores generated reasoning packages to prevent duplicate LLM calls."""
    
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl = ttl_seconds
        # Maps (retrieval_id + query_text) to (ReasoningPackage, save_timestamp)
        self._store: Dict[str, Tuple[ReasoningPackage, float]] = {}

    def _make_key(self, retrieval_id: str, query: str) -> str:
        return f"{retrieval_id}::{query.strip().lower()}"

    def lookup(self, retrieval_id: str, query: str) -> Optional[ReasoningPackage]:
        key = self._make_key(retrieval_id, query)
        entry = self._store.get(key)
        if entry:
            pkg, timestamp = entry
            # Check TTL
            if time.time() - timestamp <= self.ttl:
                return pkg
            else:
                self._store.pop(key, None)
        return None

    def save(self, retrieval_id: str, query: str, package: ReasoningPackage) -> None:
        key = self._make_key(retrieval_id, query)
        self._store[key] = (package, time.time())

    def invalidate(self, retrieval_id: str, query: str) -> None:
        key = self._make_key(retrieval_id, query)
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
export_reasoning_cache = ReasoningCache
