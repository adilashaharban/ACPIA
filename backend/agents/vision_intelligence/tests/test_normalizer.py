# -*- coding: utf-8 -*-
"""Unit tests for VisionNormalizer."""

from backend.schemas.common import BoundingBox
from backend.agents.vision_intelligence.normalizer import VisionNormalizer

def test_normalize_box_clamping() -> None:
    """Verifies that bounding boxes exceeding bounds clamp to positive dimensions."""
    # box extends beyond 1000.0 limit
    box = BoundingBox(x0=-10.0, y0=5.0, x1=1200.0, y1=15.0)
    norm = VisionNormalizer.normalize_box(box, max_width=1000.0, max_height=1000.0)
    
    assert norm.x0 == 0.0
    assert norm.x1 == 1000.0
    assert norm.y0 == 5.0
    assert norm.y1 == 15.0
