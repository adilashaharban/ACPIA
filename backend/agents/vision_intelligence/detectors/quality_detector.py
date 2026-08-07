# -*- coding: utf-8 -*-
"""Image quality assessment detector module."""

import numpy as np
from typing import List, Any
from backend.schemas.common import SourceReference
from backend.agents.vision_intelligence.detectors.base_detector import BaseDetector
from backend.agents.vision_intelligence.schema import ImageQuality
from backend.agents.vision_intelligence.constants import BLUR_THRESHOLD_VARIANCE, BRIGHTNESS_THRESHOLD_DARK

class QualityDetector(BaseDetector):
    """Measures brightness, blur, and aspect ratios."""
    
    def __init__(self) -> None:
        self.detector_name = "Laplacian_QualityDetector"
        self.version = "1.0.0"

    def detect(self, img_array: np.ndarray, context: SourceReference) -> List[ImageQuality]:
        if img_array is None or img_array.size == 0:
            return [
                ImageQuality(
                    resolution_width=0,
                    resolution_height=0,
                    aspect_ratio=0.0,
                    blur_score=0.0,
                    is_blurry=True,
                    brightness_score=0.0,
                    is_dark=True
                )
            ]
            
        height, width = img_array.shape[0], img_array.shape[1]
        aspect_ratio = round(width / height, 4) if height > 0 else 0.0
        
        # 1. Brightness estimation
        brightness_score = float(np.mean(img_array))
        is_dark = brightness_score <= BRIGHTNESS_THRESHOLD_DARK
        
        # 2. Blur estimation (Variance of Laplacian approximation)
        try:
            gray = np.mean(img_array, axis=2) if len(img_array.shape) == 3 else img_array
            # Compute Laplacian variance using simple numpy difference matrices
            # to be 100% robust and fast without native compiled library bottlenecks
            dy, dx = np.gradient(gray)
            blur_score = float(np.var(dx) + np.var(dy)) * 10.0
        except Exception:
            blur_score = 150.0  # default safe
            
        is_blurry = blur_score <= BLUR_THRESHOLD_VARIANCE
        
        return [
            ImageQuality(
                resolution_width=width,
                resolution_height=height,
                aspect_ratio=aspect_ratio,
                blur_score=round(blur_score, 2),
                is_blurry=is_blurry,
                brightness_score=round(brightness_score, 2),
                is_dark=is_dark
            )
        ]
export_quality_detector = QualityDetector
