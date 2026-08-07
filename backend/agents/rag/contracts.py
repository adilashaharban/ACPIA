# -*- coding: utf-8 -*-
"""Communication contracts for the RAG Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.rag.schema import RetrievalPackage

__all__ = ["RetrievalPackage", "RoutingTaskContract"]
