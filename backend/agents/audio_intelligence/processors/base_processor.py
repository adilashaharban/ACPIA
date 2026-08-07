# -*- coding: utf-8 -*-
"""Base processor interface."""

from abc import ABC, abstractmethod
from typing import List, Any
import numpy as np
from backend.schemas.common import SourceReference

class BaseProcessor(ABC):
    """Abstract Base Class specifying common acoustic processor methods."""
    
    @abstractmethod
    def process(self, audio_data: np.ndarray, context: SourceReference) -> List[Any]:
        """Runs acoustic features extraction or transcriptions.
        
        Args:
            audio_data: Resampled audio signal numpy array.
            context: Traceable SourceReference containing parent file metadata.
            
        Returns:
            A list containing parsed Pydantic schema objects.
        """
        pass
export_base_processor = BaseProcessor
