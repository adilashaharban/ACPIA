# -*- coding: utf-8 -*-
"""Scene classifier detector module."""

import numpy as np
from typing import List, Any
from backend.schemas.common import SourceReference
from backend.agents.vision_intelligence.detectors.base_detector import BaseDetector
from backend.agents.vision_intelligence.schema import SceneInformation, SceneType

class SceneDetector(BaseDetector):
    """Categorizes environment properties (day, night, interior)."""
    
    def __init__(self) -> None:
        self.detector_name = "Deterministic_SceneDetector"
        self.version = "1.0.0"

    def detect(self, img_array: np.ndarray, context: SourceReference) -> List[SceneInformation]:
        if img_array is None or img_array.size == 0:
            return [
                SceneInformation(
                    scene_type=SceneType.UNKNOWN,
                    confidence=1.0,
                    detector_name=self.detector_name,
                    detector_version=self.version
                )
            ]
            
        try:
            # Grayscale mean intensity
            mean_val = np.mean(img_array)
            
            if mean_val < 50.0:
                scene = SceneType.NIGHT
            elif mean_val > 200.0:
                scene = SceneType.OUTDOOR
            else:
                scene = SceneType.INDOOR
        except Exception:
            scene = SceneType.UNKNOWN
            
        return [
            SceneInformation(
                scene_type=scene,
                confidence=0.90,
                detector_name=self.detector_name,
                detector_version=self.version
            )
        ]
export_scene_detector = SceneDetector
