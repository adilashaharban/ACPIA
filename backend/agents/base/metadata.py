# -*- coding: utf-8 -*-
"""Agent capability metadata definition."""

from typing import List
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class AgentMetadata(ACPIABaseModel):
    """Pydantic model representing an agent's technical descriptors."""
    
    name: str = Field(..., description="Unique code identifier of the agent")
    version: str = Field(..., description="Semantic version string")
    description: str = Field(..., description="Short paragraph explanation of capabilities")
    supported_input_types: List[str] = Field(default_factory=list, description="MIME types or schemas accepted")
    supported_output_types: List[str] = Field(default_factory=list, description="Schemas returned in payload")
    dependencies: List[str] = Field(default_factory=list, description="System dependencies or external requirements")
