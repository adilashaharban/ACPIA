# -*- coding: utf-8 -*-
"""Event schema definitions."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class EventSchema(ACPIABaseModel):
    """Pydantic model representing an event extracted for investigation timelines."""
    
    event_id: str = Field(..., description="Unique UUID for this event")
    title: str = Field(..., description="Short summary/title of the event")
    timestamp: datetime = Field(..., description="When the event occurred")
    description: Optional[str] = Field(default=None, description="Detailed description of the event")
    source_evidence_id: str = Field(..., description="Evidence ID backing this event")
    associated_entities: List[str] = Field(default_factory=list, description="IDs of entities involved")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
