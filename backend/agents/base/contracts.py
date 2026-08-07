# -*- coding: utf-8 -*-
"""Global inter-agent messaging contracts."""

from typing import List, Dict, Any, Optional
from pydantic import Field
from backend.schemas.common import ACPIABaseModel
from backend.schemas.evidence import EvidenceMetadata

class RoutingTaskContract(ACPIABaseModel):
    """Routing instructions dictating next downstream step mappings."""
    
    agent: str = Field(..., description="Target agent name (e.g. vision)")
    priority: int = Field(default=1, description="Priority weight (lower runs first)")


class EvidencePackageContract(ACPIABaseModel):
    """The final package representation emitted by the Evidence Intake Agent."""
    
    schema_version: str = Field(default="1.0.0", description="Version of the JSON format")
    agent_version: str = Field(default="1.0.0", description="Ingestion agent version code")
    pipeline_version: str = Field(default="1.0.0", description="System pipeline version code")
    
    evidence_metadata: EvidenceMetadata = Field(..., description="Ingested file specs")
    chain_of_custody_log: List[Dict[str, Any]] = Field(default_factory=list, description="Custody trail audits")
    next_agents: List[RoutingTaskContract] = Field(default_factory=list, description="Computed routing targets list")
