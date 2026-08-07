# -*- coding: utf-8 -*-
"""Pydantic V2 schema definitions for the Timeline Intelligence Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, SourceReference

class TimelineEventType(str, Enum):
    """Investigation event categories."""
    FILE_CREATED = "FILE_CREATED"
    FILE_MODIFIED = "FILE_MODIFIED"
    PHOTO_CAPTURED = "PHOTO_CAPTURED"
    VIDEO_RECORDED = "VIDEO_RECORDED"
    AUDIO_RECORDED = "AUDIO_RECORDED"
    EMAIL_SENT = "EMAIL_SENT"
    EMAIL_RECEIVED = "EMAIL_RECEIVED"
    MESSAGE_SENT = "MESSAGE_SENT"
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"
    CALL_STARTED = "CALL_STARTED"
    CALL_ENDED = "CALL_ENDED"
    LOCATION_OBSERVED = "LOCATION_OBSERVED"
    DOCUMENT_CREATED = "DOCUMENT_CREATED"
    DOCUMENT_EDITED = "DOCUMENT_EDITED"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    PAYMENT = "PAYMENT"
    DEVICE_USED = "DEVICE_USED"
    UNKNOWN = "UNKNOWN"


class TimestampPrecision(str, Enum):
    """Granular timestamp measurements precision levels."""
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    SECOND = "SECOND"
    MILLISECOND = "MILLISECOND"
    UNKNOWN = "UNKNOWN"


class EventLocation(ACPIABaseModel):
    """Geographic or spatial coordinates associated with timeline events."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    confidence: float
    source_reference: SourceReference


class EventArtifact(ACPIABaseModel):
    """File attachment indicators linked to timeline events."""
    evidence_id: str
    artifact_type: str
    file_name: str
    source_reference: SourceReference


class TemporalRange(ACPIABaseModel):
    """Timeline duration range (e.g. calls start/ends)."""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class TimelineObservation(ACPIABaseModel):
    """Traceable observation details."""
    observation_id: str
    evidence_id: str
    raw_value: str
    confidence: float
    source_reference: SourceReference


class EventSource(ACPIABaseModel):
    """Traceable agent execution provenance block."""
    agent_name: str
    package_version: str
    processing_id: str
    evidence_id: str
    source_reference: SourceReference


class TimelineEvent(ACPIABaseModel):
    """Investigation event chronology node."""
    event_id: str
    event_type: TimelineEventType
    title: str
    description: str
    temporal_range: TemporalRange
    original_timestamp: str
    normalized_timestamp_utc: datetime
    timestamp_precision: TimestampPrecision
    timezone: str = Field(default="UTC")
    timestamp_confidence: float
    origin: EventSource
    sequence_number: int
    location: Optional[EventLocation] = None
    artifacts: List[EventArtifact] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list, description="Canonical Entity IDs")
    graph_nodes: List[str] = Field(default_factory=list, description="Graph Node IDs")
    graph_edges: List[str] = Field(default_factory=list, description="Graph Edge IDs")
    source_references: List[SourceReference] = Field(default_factory=list)
    supporting_observations: List[TimelineObservation] = Field(default_factory=list)
    confidence: float


class TimelineStatistics(ACPIABaseModel):
    """Chronology counters."""
    total_events: int
    precision_distribution: Dict[str, int] = Field(default_factory=dict)
    duration_days: float


class TimelineValidation(ACPIABaseModel):
    """Diagnostic check issues."""
    integrity_status: str = "PASS"
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ProcessorExecution(ACPIABaseModel):
    """Logs per submodule run."""
    processor_name: str
    processor_version: str
    execution_time_ms: float
    status: str


class TimelineMetrics(ACPIABaseModel):
    """Execution timing profile."""
    processing_time_ms: float
    timestamp_normalization_time_ms: float
    merge_time_ms: float
    sorting_time_ms: float
    validation_time_ms: float
    builder_time_ms: float
    executions: List[ProcessorExecution] = Field(default_factory=list)


class TimelineSummary(ACPIABaseModel):
    """Logical statistics counters."""
    event_type_distribution: Dict[str, int] = Field(default_factory=dict)
    earliest_timestamp: Optional[datetime] = None
    latest_timestamp: Optional[datetime] = None


class TimelinePackage(ACPIABaseModel):
    """Root standardized timeline package payload schema."""
    schema_version: str = "1.0.0"
    timeline_id: str
    case_id: str
    graph_id: Optional[str] = None
    timeline_version: str = "1.0.0"
    created_at: datetime
    events: List[TimelineEvent] = Field(default_factory=list)
    event_index: Dict[str, int] = Field(
        default_factory=dict,
        description="Maps event_id to chronological index for O(1) lookup."
    )
    statistics: TimelineStatistics
    validation: TimelineValidation
    metrics: TimelineMetrics
    summary: TimelineSummary
