# -*- coding: utf-8 -*-
"""Common schemas and base definitions."""

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

class ACPIABaseModel(BaseModel):
    """Common base settings for all Pydantic models in ACPIA."""
    
    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        populate_by_name = True


class ProcessingState(str, Enum):
    """Lifecyle state of evidence processing."""
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    HASHED = "HASHED"
    STORED = "STORED"
    REGISTERED = "REGISTERED"
    READY = "READY"
    FAILED = "FAILED"


class DocumentElementType(str, Enum):
    """Supported structural elements within document layouts."""
    PARAGRAPH = "PARAGRAPH"
    TABLE = "TABLE"
    TABLE_CELL = "TABLE_CELL"
    HEADER = "HEADER"
    FOOTER = "FOOTER"
    TITLE = "TITLE"
    FORM = "FORM"
    LIST = "LIST"
    IMAGE_CAPTION = "IMAGE_CAPTION"
    OCR = "OCR"


class BoundingBox(ACPIABaseModel):
    """Geometric coordinates representing visual bounding areas."""
    x0: float = Field(..., description="Top-left x coordinate")
    y0: float = Field(..., description="Top-left y coordinate")
    x1: float = Field(..., description="Bottom-right x coordinate")
    y1: float = Field(..., description="Bottom-right y coordinate")


class SourceReference(ACPIABaseModel):
    """Complete traceability context mapping text or visual detections to source locations."""
    evidence_id: str = Field(..., description="Parent evidence UUID")
    file_path: str = Field(..., description="Absolute path location of the file")
    page_number: int = Field(..., description="1-indexed page index number")
    parser: str = Field(..., description="Parser class identifier")
    parser_version: str = Field(..., description="Software version")
    source_element: DocumentElementType = Field(..., description="Structural source label")
    bounding_box: BoundingBox | None = Field(default=None)

