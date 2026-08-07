# -*- coding: utf-8 -*-
"""Unit tests for ChronologicalSorter."""

from datetime import datetime, timezone
from backend.agents.timeline_intelligence.sorter import ChronologicalSorter
from backend.agents.timeline_intelligence.schema import TimelineEvent, TimelineEventType, TemporalRange, EventSource, TimestampPrecision
from backend.schemas.common import SourceReference, DocumentElementType

def test_sorter() -> None:
    """Verifies that sorter assigns sequence numbers chronologically."""
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
        temporal_range=TemporalRange(start_time=datetime(2026, 8, 1, 10, 10, 0, tzinfo=timezone.utc)),
        original_timestamp="2026-08-01 10:10:00",
        normalized_timestamp_utc=datetime(2026, 8, 1, 10, 10, 0, tzinfo=timezone.utc),
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
        temporal_range=TemporalRange(start_time=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc)),
        original_timestamp="2026-08-01 10:00:00",
        normalized_timestamp_utc=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc),
        timestamp_precision=TimestampPrecision.SECOND,
        timestamp_confidence=1.0,
        origin=origin,
        sequence_number=0,
        confidence=1.0
    )
    
    sorted_events, index = ChronologicalSorter.sort_and_index([e1, e2])
    assert sorted_events[0].event_id == "EVT-2"
    assert sorted_events[0].sequence_number == 1
    assert sorted_events[1].event_id == "EVT-1"
    assert sorted_events[1].sequence_number == 2
    assert index["EVT-2"] == 1
