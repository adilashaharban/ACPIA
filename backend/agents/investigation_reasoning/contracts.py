# -*- coding: utf-8 -*-
"""Communication contracts for the Investigation Reasoning Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.investigation_reasoning.schema import ReasoningPackage

__all__ = ["ReasoningPackage", "RoutingTaskContract"]
