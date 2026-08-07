# -*- coding: utf-8 -*-
"""Unit tests for TimelineRepository implementations."""

from datetime import datetime, timezone
from backend.agents.timeline_intelligence.repositories.memory_repository import MemoryRepository
from backend.agents.timeline_intelligence.repositories.sqlite_repository import SQLiteRepository
from backend.agents.timeline_intelligence.schema import TimelineEvent, TimelineEventType, TemporalRange, EventSource, TimestampPrecision
from backend.schemas.common import SourceReference, DocumentElementType

def test_repositories() -> None:
    """Verifies that events save, load, and filter correctly inside Memory and SQLite backends."""
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
    
    e = TimelineEvent(
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
        sequence_number=1,
        source_references=[ref],
        entities=["ENT-1"],
        confidence=1.0
    )
    
    # Test MemoryRepository
    mem_repo = MemoryRepository()
    mem_repo.save_events([e])
    assert len(mem_repo.list_events()) == 1
    assert len(mem_repo.find_events_by_entity("ENT-1")) == 1
    assert len(mem_repo.find_events_by_entity("ENT-MISSING")) == 0
    assert len(mem_repo.find_events_by_evidence("EVID-1")) == 1
    
    # Test SQLiteRepository
    sqlite_repo = SQLiteRepository(":memory:")
    sqlite_repo.save_events([e])
    assert len(sqlite_repo.list_events()) == 1
    assert sqlite_repo.get_event("EVT-1") is not None
    assert len(sqlite_repo.find_events_by_entity("ENT-1")) == 1
    assert len(sqlite_repo.find_events_by_time_range(datetime(2026, 8, 1, 9, 0, 0, tzinfo=timezone.utc), datetime(2026, 8, 1, 11, 0, 0, tzinfo=timezone.utc))) == 1
