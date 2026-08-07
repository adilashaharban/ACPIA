# -*- coding: utf-8 -*-
"""Visual detectors package namespace."""

from backend.agents.vision_intelligence.detectors.base_detector import BaseDetector
from backend.agents.vision_intelligence.detectors.object_detector import ObjectDetector
from backend.agents.vision_intelligence.detectors.face_detector import FaceDetector
from backend.agents.vision_intelligence.detectors.vehicle_detector import VehicleDetector
from backend.agents.vision_intelligence.detectors.license_plate_detector import LicensePlateDetector
from backend.agents.vision_intelligence.detectors.scene_detector import SceneDetector
from backend.agents.vision_intelligence.detectors.color_detector import ColorDetector
from backend.agents.vision_intelligence.detectors.quality_detector import QualityDetector
from backend.agents.vision_intelligence.detectors.duplicate_detector import DuplicateDetector
from backend.agents.vision_intelligence.detectors.ocr_region_detector import OcrRegionDetector

__all__ = [
    "BaseDetector",
    "ObjectDetector",
    "FaceDetector",
    "VehicleDetector",
    "LicensePlateDetector",
    "SceneDetector",
    "ColorDetector",
    "QualityDetector",
    "DuplicateDetector",
    "OcrRegionDetector",
]
