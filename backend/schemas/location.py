# -*- coding: utf-8 -*-
"""Location schema definitions."""

from typing import Optional, Dict, Any
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class LocationSchema(ACPIABaseModel):
    """Pydantic model representing a physical location coordinate or address."""
    
    location_id: str = Field(..., description="Unique UUID for this location reference")
    name: Optional[str] = Field(default=None, description="Name of place or establishment")
    latitude: Optional[float] = Field(default=None, description="GPS Latitude")
    longitude: Optional[float] = Field(default=None, description="GPS Longitude")
    address: Optional[str] = Field(default=None, description="Full string address")
    source_evidence_id: str = Field(..., description="Evidence ID where this was extracted")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
