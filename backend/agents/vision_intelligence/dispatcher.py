# -*- coding: utf-8 -*-
"""Vision detector dispatcher."""

from typing import Dict, List, Type, Optional
from backend.agents.vision_intelligence.exceptions import UnsupportedFormatError
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
from backend.agents.vision_intelligence.constants import IMAGE_MIME_GROUPS

class VisionDispatcher:
    """Dispatches visual content to a list of coordinate scanner engines."""
    
    def __init__(self, custom_detectors: Optional[List[Type[BaseDetector]]] = None) -> None:
        """Registers default scanner engines."""
        self._detectors: List[Type[BaseDetector]] = [
            ObjectDetector,
            FaceDetector,
            VehicleDetector,
            LicensePlateDetector,
            SceneDetector,
            ColorDetector,
            QualityDetector,
            DuplicateDetector,
            OcrRegionDetector,
        ]
        if custom_detectors:
            self._detectors = custom_detectors

    def get_detectors(self, mime_type: str) -> List[Type[BaseDetector]]:
        """Resolves the registered list of detector classes.
        
        Args:
            mime_type: File signature MIME type.
            
        Returns:
            A list of detector classes inheriting BaseDetector.
            
        Raises:
            UnsupportedFormatError: If MIME type is not associated with images.
        """
        if not mime_type:
            raise UnsupportedFormatError("MIME type is empty.")
            
        normalized = mime_type.lower().strip()
        
        # Verify visual signature
        is_supported = False
        for category, mimes in IMAGE_MIME_GROUPS.items():
            if normalized in mimes:
                is_supported = True
                break
                
        if not is_supported and not normalized.startswith("image/"):
            raise UnsupportedFormatError(f"Unsupported visual MIME signature: {mime_type}")
            
        return self._detectors
