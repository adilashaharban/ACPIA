# -*- coding: utf-8 -*-
"""Unit tests for DuplicateDetector."""

from datetime import datetime, timezone
from backend.agents.timeline_intelligence.duplicate_detector import DuplicateDetector
from backend.agents.timeline_intelligence.schema import TimelineEvent, TimelineEventType, TemporalRange, EventSource, TimestampPrecision
from backend.schemas.common import SourceReference, DocumentElementType

def test_duplicate_detector() -> None:
    """Verifies that events within DUPLICATE_PROXIMITY_SECONDS are grouped."""
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
    
    e1 = TimelineEvent(
        event_id="EVT-1",
        event_type=TimelineEventType.FILE_CREATED,
        title="Created",
        description="Desc",
        temporal_range=TemporalRange(start_time=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc)),
        original_timestamp="2026-08-01 10:00:00",
        normalized_timestamp_utc=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc),
        timestamp_precision=TimestampPrecision.SECOND,
        timestamp_confidence=1.0,
        origin=origin,
        sequence_number=0,
        confidence=1.0
    )
    
    e2 = TimelineEvent(
        event_id="EVT-2",
        event_type=TimelineEventType.FILE_CREATED,
        title="Created",
        description="Desc",
        temporal_range=TemporalRange(start_time=datetime(2026, 8, 1, 10, 0, 0, 500000, tzinfo=timezone.utc)),
        original_timestamp="2026-08-01 10:00:00.5",
        normalized_timestamp_utc=datetime(2026, 8, 1, 10, 0, 0, 500000, tzinfo=timezone.utc),
        timestamp_precision=TimestampPrecision.MILLISECOND,
        timestamp_confidence=1.0,
        origin=origin,
        sequence_number=0,
        confidence=1.0
    )
    
    groups = DuplicateDetector.detect_groups([e1, e2])
    assert len(groups) == 1
    assert len(groups[0]) == 2
