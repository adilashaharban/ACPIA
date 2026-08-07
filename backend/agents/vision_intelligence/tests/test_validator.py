# -*- coding: utf-8 -*-
"""Unit tests for VisionValidator."""

import pytest
from pathlib import Path
from backend.agents.vision_intelligence.validator import VisionValidator
from backend.agents.vision_intelligence.exceptions import ChecksumMismatchError
from backend.schemas.common import BoundingBox

def test_verify_integrity_success(mock_image: Path) -> None:
    """Verifies that matching SHA hashes complete validation successfully."""
    import hashlib
    content = mock_image.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    # Should not raise exception
    VisionValidator.verify_integrity(str(mock_image.resolve()), sha256)

def test_verify_integrity_mismatch(mock_image: Path) -> None:
    """Verifies that mismatching hashes raise ChecksumMismatchError."""
    bad_hash = "wrongsha"
    with pytest.raises(ChecksumMismatchError):
        VisionValidator.verify_integrity(str(mock_image.resolve()), bad_hash)

def test_validate_detections_invalid_orientation() -> None:
    """Verifies coordinate checks flags warnings on wrong coordinate orientation."""
    # x0 > x1 represents invalid orientation
    box = BoundingBox(x0=200.0, y0=5.0, x1=50.0, y1=15.0)
    validation = VisionValidator.validate_detections([box])
    assert validation.integrity_status == "FAIL"
    assert len(validation.errors) == 1
