# -*- coding: utf-8 -*-
"""Entity extraction schema definitions."""

from typing import Optional, Dict, Any, List
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class EntitySchema(ACPIABaseModel):
    """Pydantic model representing a generic entity extracted from evidence."""
    
    entity_id: str = Field(..., description="Unique UUID for this entity")
    entity_type: str = Field(..., description="Type of entity (e.g., email, account, phone)")
    value: str = Field(..., description="The main content value of the entity")
    confidence: float = Field(default=1.0, description="Extraction confidence score (0.0 - 1.0)")
    extracted_from: str = Field(..., description="Evidence ID this entity was found in")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context info")
