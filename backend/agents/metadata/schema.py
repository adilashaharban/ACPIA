# -*- coding: utf-8 -*-
"""Pydantic V2 schema models for structured metadata outputs."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class ExtractionConfidence(str, Enum):
    """Reflects the reliability status of extracted parameters."""
    VERIFIED = "VERIFIED"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    INVALID = "INVALID"


class GPSMetadata(ACPIABaseModel):
    """Coordinates and altitude metadata extracted from media headers."""
    latitude: Optional[float] = Field(default=None, description="Latitude in decimal degrees [-90.0, 90.0]")
    longitude: Optional[float] = Field(default=None, description="Longitude in decimal degrees [-180.0, 180.0]")
    altitude: Optional[float] = Field(default=None, description="Altitude in meters above sea level")
    timestamp: Optional[datetime] = Field(default=None, description="GPS clock timestamp")
    confidence: ExtractionConfidence = Field(default=ExtractionConfidence.NOT_AVAILABLE)


class CameraMetadata(ACPIABaseModel):
    """Details about the camera equipment captured in EXIF."""
    make: Optional[str] = Field(default=None, description="Camera manufacturer name")
    model: Optional[str] = Field(default=None, description="Camera model designation")
    lens: Optional[str] = Field(default=None, description="Lens model and hardware parameters")
    software: Optional[str] = Field(default=None, description="Software or editing software string")
    confidence: ExtractionConfidence = Field(default=ExtractionConfidence.NOT_AVAILABLE)


class DeviceMetadata(ACPIABaseModel):
    """Information tracking host capture hardware devices."""
    device_id: Optional[str] = Field(default=None, description="Hardware UUID/Serial")
    os_version: Optional[str] = Field(default=None, description="Operating system software info")
    confidence: ExtractionConfidence = Field(default=ExtractionConfidence.NOT_AVAILABLE)


class ImageMetadata(ACPIABaseModel):
    """Metadata fields specific to images."""
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    orientation: Optional[int] = Field(default=None, description="EXIF orientation value (1-8)")
    color_space: Optional[str] = Field(default=None, description="Color profile name")
    gps: Optional[GPSMetadata] = Field(default=None)
    camera: Optional[CameraMetadata] = Field(default=None)


class VideoMetadata(ACPIABaseModel):
    """Metadata fields specific to videos."""
    width: int = Field(..., description="Video resolution width")
    height: int = Field(..., description="Video resolution height")
    duration_seconds: float = Field(..., description="Video play duration in seconds")
    fps: float = Field(..., description="Frames per second rate")
    video_codec: str = Field(..., description="Video decoding format (e.g. h264)")
    audio_codec: Optional[str] = Field(default=None, description="Audio track decoding format")
    bitrate_kbps: Optional[float] = Field(default=None, description="Composite stream bitrate")
    container: str = Field(..., description="Format container suffix (e.g. mp4)")


class AudioMetadata(ACPIABaseModel):
    """Metadata fields specific to standalone audio files."""
    duration_seconds: float = Field(..., description="Audio length in seconds")
    sample_rate: int = Field(..., description="Sample frequency in Hz")
    bitrate_kbps: float = Field(..., description="Audio stream bitrate")
    channels: int = Field(..., description="Audio sound channels (e.g. mono, stereo)")
    audio_codec: str = Field(..., description="Audio compression format")


class DocumentMetadata(ACPIABaseModel):
    """Metadata fields specific to documents (e.g. PDFs)."""
    page_count: int = Field(..., description="Total pages inside the document")
    author: Optional[str] = Field(default=None, description="Document author creator")
    title: Optional[str] = Field(default=None, description="Internal meta title tag")
    creation_date: Optional[datetime] = Field(default=None, description="Created timestamp")
    creator: Optional[str] = Field(default=None, description="Creation software package")
    encrypted: bool = Field(default=False, description="True if document requires password/decryption")


class FileMetadata(ACPIABaseModel):
    """Standard OS file level stats."""
    file_size_bytes: int = Field(..., description="File size in bytes")
    file_permissions: str = Field(..., description="OS permissions string")
    creation_time: Optional[datetime] = Field(default=None, description="OS file node birth time")
    modification_time: Optional[datetime] = Field(default=None, description="OS file node modification time")


class ValidationMetadata(ACPIABaseModel):
    """Tracks inconsistencies found during validation steps."""
    integrity_verification: str = Field(default="PASS", description="SHA-256 match outcome")
    issues_detected: List[str] = Field(default_factory=list, description="Warnings logged")


class MetadataSummary(ACPIABaseModel):
    """High level structural features of the extracted metadata."""
    file_type_category: str = Field(..., description="Categorization (image, video, audio, document, text)")
    has_gps: bool = Field(..., description="True if valid GPS details present")
    is_media: bool = Field(..., description="True if video, audio, or image")
    has_exif: bool = Field(..., description="True if image has EXIF markers")
    has_camera: bool = Field(..., description="True if camera make/model found")
    has_device: bool = Field(..., description="True if device details found")
    has_document_metadata: bool = Field(..., description="True if document metadata present")
    metadata_completeness: float = Field(..., description="Field population completeness score [0.0, 1.0]")


class ExtractionMetrics(ACPIABaseModel):
    """Performance metrics of the extraction process."""
    fields_extracted: int = Field(..., description="Number of populated metadata properties")
    fields_missing: int = Field(..., description="Number of null/unextracted fields")
    extractor_used: str = Field(..., description="Name of parser module utilized")
    warnings_count: int = Field(..., description="Log warnings triggered")
    processing_time_ms: float = Field(..., description="Execution runtime duration")


class MetadataPackage(ACPIABaseModel):
    """Root standard payload contract emitted by the Metadata Agent."""
    schema_version: str = Field(default="1.0.0")
    evidence_id: str = Field(..., description="UUID of parent evidence")
    summary: MetadataSummary = Field(..., description="Overview summaries")
    file_specs: FileMetadata = Field(..., description="General file specs")
    image_details: Optional[ImageMetadata] = Field(default=None)
    video_details: Optional[VideoMetadata] = Field(default=None)
    audio_details: Optional[AudioMetadata] = Field(default=None)
    document_details: Optional[DocumentMetadata] = Field(default=None)
    validation: ValidationMetadata = Field(..., description="Anomalies checking")
    metrics: ExtractionMetrics = Field(..., description="Extraction metrics")
    raw_metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw unnormalized extracted map")
