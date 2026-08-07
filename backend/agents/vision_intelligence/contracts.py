# -*- coding: utf-8 -*-
"""Communication contracts for the Vision Intelligence Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.vision_intelligence.schema import VisionPackage

__all__ = ["VisionPackage", "RoutingTaskContract"]
