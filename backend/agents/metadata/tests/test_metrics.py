# -*- coding: utf-8 -*-
"""Unit tests for MetadataMetricsCalculator."""

import pytest
from backend.agents.metadata.metrics import MetadataMetricsCalculator
from backend.agents.metadata.schema import ImageMetadata

def test_metrics_calculator_image() -> None:
    """Verifies image metrics calculates counts and ratios correctly."""
    # 6 attributes inside ImageMetadata schema: width, height, orientation, color_space, gps, camera
    # We populate: width, height, color_space, orientation (4 fields)
    img_meta = ImageMetadata(
        width=1920,
        height=1080,
        color_space="sRGB",
        orientation=1
    )
    
    metrics, summary = MetadataMetricsCalculator.calculate(
        category="image",
        extractor_name="ImageExtractor",
        details_obj=img_meta,
        warnings_count=1,
        processing_time_ms=10.5
    )
    
    assert metrics.extractor_used == "ImageExtractor"
    assert metrics.fields_extracted == 4
    # orientation, color_space, width, height are populated; gps, camera are None (2 missing)
    assert metrics.fields_missing == 2
    assert summary.metadata_completeness == pytest.approx(4.0 / 6.0, abs=1e-4)
    assert summary.file_type_category == "image"
    assert summary.has_exif is True
    assert summary.has_gps is False
