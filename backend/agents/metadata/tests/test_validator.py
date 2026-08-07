# -*- coding: utf-8 -*-
"""Unit tests for MetadataValidator."""

import pytest
from pathlib import Path
from backend.agents.metadata.validator import MetadataValidator
from backend.agents.metadata.exceptions import ChecksumMismatchError
from backend.agents.metadata.schema import GPSMetadata, ImageMetadata, ExtractionConfidence

def test_verify_integrity_success(mock_jpeg: Path) -> None:
    """Verifies that matching SHA-256 completes without error."""
    import hashlib
    file_bytes = mock_jpeg.read_bytes()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    
    # Should not raise exception
    MetadataValidator.verify_integrity(str(mock_jpeg.resolve()), sha256)

def test_verify_integrity_mismatch(mock_jpeg: Path) -> None:
    """Verifies checksum mismatch triggers ChecksumMismatchError."""
    bad_hash = "c0ffee1234567890abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdef"
    with pytest.raises(ChecksumMismatchError):
        MetadataValidator.verify_integrity(str(mock_jpeg.resolve()), bad_hash)

def test_validate_metadata_gps_bounds() -> None:
    """Verifies warning triggers for latitude/longitude out of range values."""
    gps = GPSMetadata(
        latitude=100.0,  # Invalid, max is 90
        longitude=-200.0, # Invalid, min is -180
        confidence=ExtractionConfidence.VERIFIED
    )
    img_meta = ImageMetadata(width=100, height=100, gps=gps)
    
    validation = MetadataValidator.validate_metadata(
        file_path="mock.jpg",
        file_type="image/jpeg",
        raw_meta={},
        image_meta=img_meta
    )
    
    assert len(validation.issues_detected) == 2
    assert "Latitude 100.0 out of bounds" in validation.issues_detected[0]
    assert "Longitude -200.0 out of bounds" in validation.issues_detected[1]
