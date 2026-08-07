# -*- coding: utf-8 -*-
"""Base detector interface."""

from abc import ABC, abstractmethod
from typing import List, Any
import numpy as np
from backend.schemas.common import SourceReference

class BaseDetector(ABC):
    """Abstract Base Class specifying common visual scanner methods."""
    
    @abstractmethod
    def detect(self, img_array: np.ndarray, context: SourceReference) -> List[Any]:
        """Runs image feature extraction scans.
        
        Args:
            img_array: OpenCV image represented as an N-dimensional numpy array.
            context: Traceable SourceReference containing parent file metadata.
            
        Returns:
            A list containing parsed Pydantic schema objects.
        """
        pass
export_base_detector = BaseDetector
