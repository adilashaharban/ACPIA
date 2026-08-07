# -*- coding: utf-8 -*-
"""Communication contracts for the Entity Resolution Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.entity_resolution.schema import EntityResolutionPackage

__all__ = ["EntityResolutionPackage", "RoutingTaskContract"]
