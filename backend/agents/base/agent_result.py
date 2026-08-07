# -*- coding: utf-8 -*-
"""Execution results wrapper schema for agents."""

from typing import Dict, Any, List
from pydantic import Field
from backend.schemas.common import ACPIABaseModel
from backend.agents.base.processing_context import ProcessingContextContract

class AgentResultContract(ACPIABaseModel):
    """Enforces standard schema response wrap for all ACPIA agents."""
    
    agent: str = Field(..., description="Name of the agent generating this result")
    status: str = Field(..., description="Status execution flag (SUCCESS, FAILURE, WARNING)")
    processing_context: ProcessingContextContract = Field(..., description="Tracing context of this run")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Agent execution output payload")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance timing stats")
    warnings: List[str] = Field(default_factory=list, description="List of minor execution warning details")
    errors: List[str] = Field(default_factory=list, description="List of error trace messages if failed")
