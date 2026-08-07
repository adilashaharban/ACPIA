# -*- coding: utf-8 -*-
"""Internal Pydantic models for the Evidence Intake Agent."""

from typing import Optional
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class IngestionParams(ACPIABaseModel):
    """Parameters passed to the ingestion pipeline runtime."""
    
    file_bytes: bytes = Field(..., description="Raw file contents in bytes")
    filename: str = Field(..., description="Original name of the uploaded file")
    case_id: str = Field(..., description="Target Case ID for case association")
    uploader: str = Field(..., description="Identify the user executing the ingest")
