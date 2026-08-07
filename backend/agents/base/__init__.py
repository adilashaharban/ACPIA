# -*- coding: utf-8 -*-
"""ACPIA Base Agent Namespace."""

from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.base.agent_result import AgentResultContract
from backend.agents.base.metadata import AgentMetadata
from backend.agents.base.manifest import AgentManifest
from backend.agents.base.contracts import RoutingTaskContract, EvidencePackageContract
from backend.agents.base.base_agent import BaseAgent

__all__ = [
    "ProcessingContextContract",
    "AgentResultContract",
    "AgentMetadata",
    "AgentManifest",
    "RoutingTaskContract",
    "EvidencePackageContract",
    "BaseAgent",
]
