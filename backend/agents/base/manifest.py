# -*- coding: utf-8 -*-
"""Agent manifest schema representation."""

from typing import List, Dict, Any
from pydantic import Field
from backend.schemas.common import ACPIABaseModel
from backend.agents.base.metadata import AgentMetadata

class AgentManifest(ACPIABaseModel):
    """Pydantic model representing an agent registration manifest."""
    
    metadata: AgentMetadata = Field(..., description="Technical metadata descriptors")
    capabilities: List[str] = Field(default_factory=list, description="Text descriptors of what tasks it can perform")
    custom_configuration_schema: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Json schema for environment options/overrides"
    )
