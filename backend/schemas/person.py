# -*- coding: utf-8 -*-
"""Person profile schema definitions."""

from typing import Optional, Dict, Any, List
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class PersonSchema(ACPIABaseModel):
    """Pydantic model representing a person profile."""
    
    person_id: str = Field(..., description="Unique UUID for this person profile")
    display_name: str = Field(..., description="Calculated display name or alias")
    aliases: List[str] = Field(default_factory=list, description="All identified usernames or aliases")
    contact_details: Dict[str, str] = Field(default_factory=dict, description="Phone numbers, emails, etc.")
    source_evidence_ids: List[str] = Field(default_factory=list, description="Evidence files linking to this profile")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")

