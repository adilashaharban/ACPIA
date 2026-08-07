# -*- coding: utf-8 -*-
"""Unit tests for TimestampNormalizer."""

import pytest
from datetime import datetime, timezone
from backend.agents.timeline_intelligence.timestamp_normalizer import TimestampNormalizer
from backend.agents.timeline_intelligence.exceptions import TimestampNormalizationError
from backend.agents.timeline_intelligence.schema import TimestampPrecision

def test_timestamp_normalization() -> None:
    """Verifies that naive and offset datetimes parse to UTC correctly."""
    t1 = TimestampNormalizer.normalize("2026-08-01 10:00:00")
    assert t1.tzinfo == timezone.utc
    assert t1.hour == 10
    
    t2 = TimestampNormalizer.normalize("2026-08-01T12:00:00+02:00")
    assert t2.hour == 10  # shifted back by 2 hours
    
    with pytest.raises(TimestampNormalizationError):
        TimestampNormalizer.normalize("")

def test_infer_precision() -> None:
    """Verifies that precision inferences map year/month correctly."""
    assert TimestampNormalizer.infer_precision("2026") == TimestampPrecision.YEAR
    assert TimestampNormalizer.infer_precision("2026-08") == TimestampPrecision.MONTH
    assert TimestampNormalizer.infer_precision("2026-08-01 10:00:00.123") == TimestampPrecision.MILLISECOND
    assert TimestampNormalizer.infer_precision("2026-08-01 10:00:00") == TimestampPrecision.SECOND
stream_infer_precision = test_infer_precision
