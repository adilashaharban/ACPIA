# -*- coding: utf-8 -*-
"""Evidence Ingest specific communication contracts."""

from backend.agents.base.contracts import EvidencePackageContract, RoutingTaskContract

# Re-expose base contracts for clean importing across agents
__all__ = ["EvidencePackageContract", "RoutingTaskContract"]
