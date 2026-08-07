# -*- coding: utf-8 -*-
"""Unit tests for VisionDispatcher."""

import pytest
from backend.agents.vision_intelligence.dispatcher import VisionDispatcher
from backend.agents.vision_intelligence.exceptions import UnsupportedFormatError
from backend.agents.vision_intelligence.detectors.object_detector import ObjectDetector

def test_dispatcher_valid_mime() -> None:
    """Verifies that image/jpeg returns the list of registered detector classes."""
    dispatcher = VisionDispatcher()
    detectors = dispatcher.get_detectors("image/jpeg")
    assert len(detectors) > 0
    assert ObjectDetector in detectors

def test_dispatcher_invalid_mime() -> None:
    """Verifies that non-image MIME formats raise UnsupportedFormatError."""
    dispatcher = VisionDispatcher()
    with pytest.raises(UnsupportedFormatError):
        dispatcher.get_detectors("text/plain")
