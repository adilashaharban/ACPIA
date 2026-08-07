# -*- coding: utf-8 -*-
"""Evidence-specific schema definitions."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, ProcessingState

class EvidenceMetadata(ACPIABaseModel):
    """Pydantic model representing evidence metadata and stats."""
    
    evidence_id: str = Field(..., description="Unique UUID generated for the evidence file")
    case_id: str = Field(..., description="Case ID this evidence belongs to")
    uploader: str = Field(..., description="Name or identifier of the uploader")
    file_path: str = Field(..., description="Hashed local file path of the evidence")
    object_storage_path: str = Field(..., description="Simulated/cloud storage target path")
    sha256_hash: str = Field(..., description="SHA-256 integrity signature of the file")
    mime_type: str = Field(..., description="Detected MIME type (e.g. image/png)")
    upload_timestamp: datetime = Field(..., description="Timestamp of the ingestion")
    validation_status: ProcessingState = Field(..., description="The verified validation step status")
    processing_status: str = Field(..., description="Current processing state of the evidence")
    routing_hints: Optional[List[Dict[str, Any]]] = Field(default=None, description="Hints for routing coordinator")
    integrity_info: Optional[Dict[str, Any]] = Field(default=None, description="Hash validation metadata")
