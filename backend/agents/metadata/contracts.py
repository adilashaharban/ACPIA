# -*- coding: utf-8 -*-
"""Communication contracts for the Metadata Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.metadata.schema import MetadataPackage

# Export schemas used by downstream consumer agents
__all__ = ["MetadataPackage", "RoutingTaskContract"]
