# -*- coding: utf-8 -*-
"""Communication contracts for the Audio Intelligence Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.audio_intelligence.schema import AudioPackage

__all__ = ["AudioPackage", "RoutingTaskContract"]
