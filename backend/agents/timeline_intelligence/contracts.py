# -*- coding: utf-8 -*-
"""Communication contracts for the Timeline Intelligence Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.timeline_intelligence.schema import TimelinePackage

__all__ = ["TimelinePackage", "RoutingTaskContract"]
