# -*- coding: utf-8 -*-
"""Pydantic V2 schema definitions for the Vision Intelligence Agent."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, BoundingBox, SourceReference

class SceneType(str, Enum):
    """Enums representing visual indoor/outdoor classifications."""
    INDOOR = "INDOOR"
    OUTDOOR = "OUTDOOR"
    NIGHT = "NIGHT"
    DAY = "DAY"
    VEHICLE_INTERIOR = "VEHICLE_INTERIOR"
    UNKNOWN = "UNKNOWN"


class VehicleType(str, Enum):
    """Supported vehicle categories."""
    CAR = "CAR"
    TRUCK = "TRUCK"
    BUS = "BUS"
    MOTORBIKE = "MOTORBIKE"
    BICYCLE = "BICYCLE"
    UNKNOWN = "UNKNOWN"


class FeatureType(str, Enum):
    """Visual feature attribute classification categories."""
    COLOR = "COLOR"
    LOGO = "LOGO"
    CLOTHING_COLOR = "CLOTHING_COLOR"
    SCENE_ATTRIBUTE = "SCENE_ATTRIBUTE"
    TEXT_REGION = "TEXT_REGION"
    QUALITY = "QUALITY"


class Polygon(ACPIABaseModel):
    """Multi-point geometric area boundary."""
    points: List[tuple[float, float]] = Field(default_factory=list, description="Coordinate polygon boundary")


class VisualFeature(ACPIABaseModel):
    """Consolidated visual feature descriptors for Correlation and ER downstream agents."""
    feature_id: str = Field(..., description="Unique generated UUID for feature")
    feature_type: FeatureType = Field(..., description="Feature category type")
    value: str = Field(..., description="Feature string value")
    confidence: float = Field(default=1.0)
    source_reference: SourceReference = Field(..., description="Audit traceability link")


class DetectedObject(ACPIABaseModel):
    """Standardized general detected object model."""
    object_id: str = Field(..., description="Object identifier")
    class_id: int = Field(..., description="Integer category ID from detector model")
    class_name: str = Field(..., description="String classification label")
    confidence: float
    bounding_box: BoundingBox
    source_reference: SourceReference
    detector_name: str
    detector_version: str
    frame_number: Optional[int] = None


class DetectedPerson(ACPIABaseModel):
    """Person detection attributes (no personal name identities)."""
    person_id: str
    confidence: float
    bounding_box: BoundingBox
    clothing_colors: List[str] = Field(default_factory=list)
    source_reference: SourceReference
    detector_name: str
    detector_version: str
    frame_number: Optional[int] = None


class DetectedFace(ACPIABaseModel):
    """Facial region detection details (strictly detection only, no recognition)."""
    face_id: str
    confidence: float
    bounding_box: BoundingBox
    source_reference: SourceReference
    detector_name: str
    detector_version: str
    frame_number: Optional[int] = None


class DetectedVehicle(ACPIABaseModel):
    """Vehicle detection details."""
    vehicle_id: str
    vehicle_type: VehicleType
    confidence: float
    bounding_box: BoundingBox
    source_reference: SourceReference
    detector_name: str
    detector_version: str
    frame_number: Optional[int] = None


class DetectedLicensePlate(ACPIABaseModel):
    """License plate localization coordinates (no OCR reading)."""
    plate_id: str
    confidence: float
    bounding_box: BoundingBox
    source_reference: SourceReference
    detector_name: str
    detector_version: str
    frame_number: Optional[int] = None


class SceneInformation(ACPIABaseModel):
    """Scene classification attributes."""
    scene_type: SceneType
    confidence: float
    detector_name: str
    detector_version: str


class ImageQuality(ACPIABaseModel):
    """No-reference quality assessment metrics."""
    resolution_width: int
    resolution_height: int
    aspect_ratio: float
    blur_score: float
    is_blurry: bool
    brightness_score: float
    is_dark: bool


class OCRRegion(ACPIABaseModel):
    """Text-containing graphic area coordinates (does not store extracted text)."""
    region_id: str
    bounding_box: BoundingBox
    confidence: float
    text_present: bool = Field(default=True, description="Flag indicating image contains text regions")
    source_reference: SourceReference


class ColorInformation(ACPIABaseModel):
    """Dominant color extraction metrics."""
    dominant_colors: List[str] = Field(default_factory=list, description="List of hex colors")
    color_palette_name: Optional[str] = None


class VisualStatistics(ACPIABaseModel):
    """Counts of identified elements."""
    object_count: int
    person_count: int
    face_count: int
    vehicle_count: int
    ocr_region_count: int


class VisionValidation(ACPIABaseModel):
    """Diagnostic check issues."""
    integrity_status: str = "PASS"
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class DetectorExecution(ACPIABaseModel):
    """Richer execution logs per detector engine."""
    detector_name: str
    detector_version: str
    execution_time_ms: float
    status: str


class VisionMetrics(ACPIABaseModel):
    """Consolidated performance profile."""
    processing_time_ms: float
    executions: List[DetectorExecution] = Field(default_factory=list)


class VisionSummary(ACPIABaseModel):
    """High level content indices."""
    mime_type: str
    has_faces: bool
    has_vehicles: bool
    has_text: bool
    perceptual_hash: str
    duplicate_group_id: Optional[str] = Field(default=None, description="Duplicate group cluster hash ID")


class VisionPackage(ACPIABaseModel):
    """Root standardized visual results schema."""
    schema_version: str = "1.0.0"
    evidence_id: str
    summary: VisionSummary
    objects: List[DetectedObject] = Field(default_factory=list)
    people: List[DetectedPerson] = Field(default_factory=list)
    faces: List[DetectedFace] = Field(default_factory=list)
    vehicles: List[DetectedVehicle] = Field(default_factory=list)
    plates: List[DetectedLicensePlate] = Field(default_factory=list)
    ocr_regions: List[OCRRegion] = Field(default_factory=list)
    features: List[VisualFeature] = Field(default_factory=list)
    scene: SceneInformation
    quality: ImageQuality
    colors: ColorInformation
    statistics: VisualStatistics
    validation: VisionValidation
    metrics: VisionMetrics
