# -*- coding: utf-8 -*-
"""Unit tests for TimelineValidator."""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from backend.agents.timeline_intelligence.validator import TimelineValidator
from backend.agents.timeline_intelligence.exceptions import ChecksumMismatchError
from backend.agents.timeline_intelligence.schema import TimelineEvent, TimelineEventType, TemporalRange, EventSource, TimestampPrecision
from backend.schemas.common import SourceReference, DocumentElementType

def test_verify_integrity_success(mock_evidence_file: Path) -> None:
    """Verifies SHA checksums validation."""
    import hashlib
    content = mock_evidence_file.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    TimelineValidator.verify_integrity(str(mock_evidence_file.resolve()), sha256)

def test_verify_integrity_mismatch(mock_evidence_file: Path) -> None:
    """Verifies that mismatching checksums raise ChecksumMismatchError."""
    with pytest.raises(ChecksumMismatchError):
        TimelineValidator.verify_integrity(str(mock_evidence_file.resolve()), "badsha")

def test_validate_timeline() -> None:
    """Verifies sequence validations and UTC check rules."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    origin = EventSource(
        agent_name="test",
        package_version="1.0.0",
        processing_id="p1",
        evidence_id="EVID-1",
        source_reference=ref
    )
    
    # Event 2 has a timestamp earlier than Event 1, but follows it in the array
    e1 = TimelineEvent(
        event_id="EVT-1",
        event_type=TimelineEventType.FILE_CREATED,
        title="Created",
        description="Desc",
        temporal_range=TemporalRange(start_time=datetime(2026, 8, 1, 10, 10, 0, tzinfo=timezone.utc)),
        original_timestamp="2026-08-01 10:10:00",
        normalized_timestamp_utc=datetime(2026, 8, 1, 10, 10, 0, tzinfo=timezone.utc),
        timestamp_precision=TimestampPrecision.SECOND,
        timestamp_confidence=1.0,
        origin=origin,
        sequence_number=1,
        confidence=1.0
    )
    
    e2 = TimelineEvent(
        event_id="EVT-2",
        event_type=TimelineEventType.FILE_CREATED,
        title="Created",
        description="Desc",
        temporal_range=TemporalRange(start_time=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc)),
        original_timestamp="2026-08-01 10:00:00",
        normalized_timestamp_utc=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc),
        timestamp_precision=TimestampPrecision.SECOND,
        timestamp_confidence=1.0,
        origin=origin,
        sequence_number=2,
        confidence=1.0
    )
    
    validation = TimelineValidator.validate_timeline([e1, e2])
    assert validation.integrity_status == "FAIL"
    assert len(validation.errors) == 1
    assert "sorting constraint broken" in validation.errors[0]
