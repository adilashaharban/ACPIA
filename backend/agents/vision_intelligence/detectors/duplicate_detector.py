# -*- coding: utf-8 -*-
"""Duplicate detector module using imagehash."""

from typing import List, Any
import numpy as np
from PIL import Image
import imagehash
from backend.schemas.common import SourceReference
from backend.agents.vision_intelligence.detectors.base_detector import BaseDetector

class DuplicateDetector(BaseDetector):
    """Computes perceptual phashes to identify exact or near-identical duplicate files."""
    
    def __init__(self) -> None:
        self.detector_name = "PerceptualHash_Detector"
        self.version = "1.0.0"

    def detect(self, img_array: np.ndarray, context: SourceReference) -> List[str]:
        """Calculates the perceptual hash of the image.
        
        Args:
            img_array: NDArray image.
            context: Trace reference.
            
        Returns:
            A list containing the perceptual hash hex string representation.
        """
        if img_array is None or img_array.size == 0:
            return ["0000000000000000"]
            
        try:
            pil_img = Image.fromarray(img_array.astype(np.uint8))
            h = imagehash.phash(pil_img)
            phash_str = str(h)
        except Exception:
            phash_str = "8080808080808080"
            
        return [phash_str]
export_duplicate_detector = DuplicateDetector
