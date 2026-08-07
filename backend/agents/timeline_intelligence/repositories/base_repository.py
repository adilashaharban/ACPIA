# -*- coding: utf-8 -*-
"""Timeline repository base interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from backend.agents.timeline_intelligence.schema import TimelineEvent

class TimelineRepository(ABC):
    """Abstract interface for storing and loading timeline chronologies."""
    
    @abstractmethod
    def save_events(self, events: List[TimelineEvent]) -> None:
        """Stores a list of timeline events."""
        pass

    @abstractmethod
    def load_events(self) -> List[TimelineEvent]:
        """Loads and returns all saved events."""
        pass

    @abstractmethod
    def clear_timeline(self) -> None:
        """Purges stored events."""
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Optional[TimelineEvent]:
        """Loads a single event by ID."""
        pass

    @abstractmethod
    def list_events(self) -> List[TimelineEvent]:
        """Lists all events in chronological sequence."""
        pass

    @abstractmethod
    def find_events_by_entity(self, entity_id: str) -> List[TimelineEvent]:
        """Filters events associated with a Canonical Entity ID."""
        pass

    @abstractmethod
    def find_events_by_time_range(self, start: datetime, end: datetime) -> List[TimelineEvent]:
        """Filters events within time window constraints."""
        pass

    @abstractmethod
    def find_events_by_evidence(self, evidence_id: str) -> List[TimelineEvent]:
        """Filters events originating from a target evidence file."""
        pass
export_base_repository = TimelineRepository
