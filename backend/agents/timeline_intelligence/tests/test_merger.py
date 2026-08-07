# -*- coding: utf-8 -*-
"""Unit tests for EventMerger."""

from datetime import datetime, timezone
from backend.agents.timeline_intelligence.merger import EventMerger
from backend.agents.timeline_intelligence.schema import TimelineEvent, TimelineEventType, TemporalRange, EventSource, TimestampPrecision
from backend.schemas.common import SourceReference, DocumentElementType

def test_merger() -> None:
    """Verifies that duplicate fields merge collections."""
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
        entities=["ENT-1"],
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
        timestamp_confidence=0.8,
        origin=origin,
        sequence_number=0,
        entities=["ENT-2"],
        confidence=0.8
    )
    
    merged = EventMerger.merge_events([e1, e2])
    assert len(merged.entities) == 2
    assert "ENT-1" in merged.entities
    assert "ENT-2" in merged.entities
    assert merged.confidence == 0.90  # average of 1.0 and 0.8
