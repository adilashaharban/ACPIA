# -*- coding: utf-8 -*-
"""Unit tests for MetadataNormalizer."""

import pytest
from datetime import datetime, timezone
from backend.agents.metadata.normalizer import MetadataNormalizer

def test_normalize_date_valid_string() -> None:
    """Verifies standard EXIF colon-format strings are converted to aware datetimes."""
    date_str = "2026:08:06 15:30:00"
    normalized = MetadataNormalizer.normalize_date(date_str)
    assert normalized == datetime(2026, 8, 6, 15, 30, 0, tzinfo=timezone.utc)

def test_normalize_date_invalid() -> None:
    """Verifies that unparseable date strings return None."""
    assert MetadataNormalizer.normalize_date("invalid-date-string") is None

def test_normalize_gps_north_east() -> None:
    """Verifies GPS coordinates are correctly converted to positive decimal degrees."""
    # 37° 46' 30" N
    val = MetadataNormalizer.normalize_gps(37, 46, 30, "N")
    assert val == pytest.approx(37.775)

def test_normalize_gps_south_west() -> None:
    """Verifies GPS coordinates in South/West references negate output."""
    # 122° 25' 10" W
    val = MetadataNormalizer.normalize_gps(122, 25, 10, "W")
    assert val == pytest.approx(-122.419444)

def test_normalize_codec_standards() -> None:
    """Verifies canonical naming resolutions of audio/video streams."""
    assert MetadataNormalizer.normalize_codec("avc1") == "H.264/AVC"
    assert MetadataNormalizer.normalize_codec("hevc") == "H.265/HEVC"
    assert MetadataNormalizer.normalize_codec("mp4a") == "AAC"
    assert MetadataNormalizer.normalize_codec("unknown_codec") == "UNKNOWN_CODEC"
