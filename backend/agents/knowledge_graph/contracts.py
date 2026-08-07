# -*- coding: utf-8 -*-
"""Communication contracts for the Knowledge Graph Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.knowledge_graph.schema import KnowledgeGraphPackage

__all__ = ["KnowledgeGraphPackage", "RoutingTaskContract"]
