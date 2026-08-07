# -*- coding: utf-8 -*-
"""Vision coordinate normalizer."""

from backend.schemas.common import BoundingBox

class VisionNormalizer:
    """Clamps coordinate ranges and standardizes visual bounding boxes."""
    
    @staticmethod
    def normalize_box(box: BoundingBox, max_width: float = 1000.0, max_height: float = 1000.0) -> BoundingBox:
        """Clamps coordinate properties to positive boundaries.
        
        Args:
            box: BoundingBox object.
            max_width: Maximum boundary.
            max_height: Maximum boundary.
            
        Returns:
            A new clamped BoundingBox object.
        """
        # Clamp coordinate values between [0, max]
        x0 = max(0.0, min(box.x0, max_width))
        y0 = max(0.0, min(box.y0, max_height))
        x1 = max(x0, min(box.x1, max_width))
        y1 = max(y0, min(box.y1, max_height))
        
        return BoundingBox(
            x0=round(x0, 2),
            y0=round(y0, 2),
            x1=round(x1, 2),
            y1=round(y1, 2)
        )
