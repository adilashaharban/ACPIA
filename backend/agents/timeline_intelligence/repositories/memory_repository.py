# -*- coding: utf-8 -*-
"""In-memory timeline repository implementation."""

from typing import List, Optional, Dict
from datetime import datetime
from backend.agents.timeline_intelligence.repositories.base_repository import TimelineRepository
from backend.agents.timeline_intelligence.schema import TimelineEvent

class MemoryRepository(TimelineRepository):
    """Stores timeline events inside thread-safe local dictionaries."""
    
    def __init__(self) -> None:
        self._events: Dict[str, TimelineEvent] = {}

    def save_events(self, events: List[TimelineEvent]) -> None:
        for event in events:
            self._events[event.event_id] = event

    def load_events(self) -> List[TimelineEvent]:
        # Return sorted list chronologically
        return sorted(self._events.values(), key=lambda x: x.normalized_timestamp_utc)

    def clear_timeline(self) -> None:
        self._events.clear()

    def get_event(self, event_id: str) -> Optional[TimelineEvent]:
        return self._events.get(event_id)

    def list_events(self) -> List[TimelineEvent]:
        return self.load_events()

    def find_events_by_entity(self, entity_id: str) -> List[TimelineEvent]:
        return [e for e in self.load_events() if entity_id in e.entities]

    def find_events_by_time_range(self, start: datetime, end: datetime) -> List[TimelineEvent]:
        return [e for e in self.load_events() if start <= e.normalized_timestamp_utc <= end]

    def find_events_by_evidence(self, evidence_id: str) -> List[TimelineEvent]:
        return [e for e in self.load_events() if any(ref.evidence_id == evidence_id for ref in e.source_references)]
export_memory_repository = MemoryRepository
