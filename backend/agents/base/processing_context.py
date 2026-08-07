# -*- coding: utf-8 -*-
"""Execution tracing context schema for agents."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class ProcessingContextContract(ACPIABaseModel):
    """Context object identifying case runs, tracing IDs, and stages."""
    
    processing_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Trace execution UUID")
    case_id: str = Field(..., description="Investigation Case Identifier")
    evidence_id: Optional[str] = Field(default=None, description="Active target evidence UUID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Context creation time")
    pipeline_stage: str = Field(..., description="Current agent/step name")
