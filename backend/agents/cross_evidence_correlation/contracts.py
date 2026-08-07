# -*- coding: utf-8 -*-
"""Communication contracts for the Cross-Evidence Correlation Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.cross_evidence_correlation.schema import CorrelationPackage

__all__ = ["CorrelationPackage", "RoutingTaskContract"]
