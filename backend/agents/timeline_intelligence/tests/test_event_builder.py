# -*- coding: utf-8 -*-
"""Unit tests for EventBuilder."""

from datetime import datetime, timezone
from backend.agents.timeline_intelligence.event_builder import EventBuilder
from backend.agents.timeline_intelligence.schema import TimelineEventType, TimestampPrecision
from backend.schemas.common import SourceReference, DocumentElementType

def test_event_builder() -> None:
    """Verifies candidate mapping standardizes outputs."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    cand = {
        "event_type": TimelineEventType.FILE_CREATED,
        "title": "Created",
        "description": "Desc",
        "raw_timestamp": "2026-08-01 10:00:00",
        "confidence": 1.0,
        "source_reference": ref,
        "location": {"latitude": 12.97, "longitude": 77.59, "address": "Bengaluru"},
        "artifacts": [{"evidence_id": "E1", "artifact_type": "FILE", "file_name": "a.txt"}]
    }
    
    norm_time = datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc)
    precision = TimestampPrecision.SECOND
    
    event = EventBuilder.build_event(cand, "p1", norm_time, precision)
    assert event.event_type == TimelineEventType.FILE_CREATED
    assert event.location is not None
    assert event.location.latitude == 12.97
    assert len(event.artifacts) == 1
    assert event.artifacts[0].file_name == "a.txt"
