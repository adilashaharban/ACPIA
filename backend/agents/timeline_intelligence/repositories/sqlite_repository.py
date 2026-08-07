# -*- coding: utf-8 -*-
"""SQLite-backed timeline repository implementation."""

import json
import sqlite3
from typing import List, Optional
from datetime import datetime
from backend.agents.timeline_intelligence.repositories.base_repository import TimelineRepository
from backend.agents.timeline_intelligence.schema import TimelineEvent
from backend.agents.timeline_intelligence.exceptions import RepositoryError

class SQLiteRepository(TimelineRepository):
    """Stores timeline events inside a local SQLite database."""
    
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        try:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS timeline_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    timestamp TEXT,
                    event_data TEXT
                )"""
            )
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to initialize SQLite timeline database: {e}")

    def save_events(self, events: List[TimelineEvent]) -> None:
        try:
            for event in events:
                self.conn.execute(
                    "INSERT OR REPLACE INTO timeline_events (event_id, event_type, timestamp, event_data) VALUES (?, ?, ?, ?)",
                    (
                        event.event_id,
                        event.event_type.name,
                        event.normalized_timestamp_utc.isoformat(),
                        event.model_dump_json()
                    )
                )
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to save events to SQLite: {e}")

    def load_events(self) -> List[TimelineEvent]:
        try:
            events = []
            cursor = self.conn.execute("SELECT event_data FROM timeline_events ORDER BY datetime(timestamp) ASC")
            for row in cursor.fetchall():
                events.append(TimelineEvent.model_validate_json(row[0]))
            return events
        except Exception as e:
            raise RepositoryError(f"Failed to load events from SQLite: {e}")

    def clear_timeline(self) -> None:
        try:
            self.conn.execute("DELETE FROM timeline_events")
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to clear SQLite timeline: {e}")

    def get_event(self, event_id: str) -> Optional[TimelineEvent]:
        try:
            cursor = self.conn.execute("SELECT event_data FROM timeline_events WHERE event_id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                return TimelineEvent.model_validate_json(row[0])
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to fetch event {event_id} from SQLite: {e}")

    def list_events(self) -> List[TimelineEvent]:
        return self.load_events()

    def find_events_by_entity(self, entity_id: str) -> List[TimelineEvent]:
        return [e for e in self.load_events() if entity_id in e.entities]

    def find_events_by_time_range(self, start: datetime, end: datetime) -> List[TimelineEvent]:
        return [e for e in self.load_events() if start <= e.normalized_timestamp_utc <= end]

    def find_events_by_evidence(self, evidence_id: str) -> List[TimelineEvent]:
        return [e for e in self.load_events() if any(ref.evidence_id == evidence_id for ref in e.source_references)]


export_sqlite_repository = SQLiteRepository

