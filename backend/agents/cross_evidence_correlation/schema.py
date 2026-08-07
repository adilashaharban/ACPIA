# -*- coding: utf-8 -*-
"""Pydantic V2 schema definitions for the Cross-Evidence Correlation Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, SourceReference

class CorrelationType(str, Enum):
    """Correlation category type enum."""
    ENTITY_MATCH = "ENTITY_MATCH"
    TEMPORAL_MATCH = "TEMPORAL_MATCH"
    LOCATION_MATCH = "LOCATION_MATCH"
    FILE_MATCH = "FILE_MATCH"
    CONTENT_MATCH = "CONTENT_MATCH"
    VISUAL_MATCH = "VISUAL_MATCH"
    AUDIO_MATCH = "AUDIO_MATCH"
    DOCUMENT_MATCH = "DOCUMENT_MATCH"
    GRAPH_MATCH = "GRAPH_MATCH"
    COMPOSITE_MATCH = "COMPOSITE_MATCH"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN"


class CorrelationStrength(str, Enum):
    """Calculated strength indicator enum."""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    EXACT = "EXACT"


class ConflictType(str, Enum):
    """Identified conflict category enum."""
    LOCATION_CONFLICT = "LOCATION_CONFLICT"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    ENTITY_CONFLICT = "ENTITY_CONFLICT"
    GRAPH_CONFLICT = "GRAPH_CONFLICT"
    DUPLICATE_CONFLICT = "DUPLICATE_CONFLICT"
    UNKNOWN = "UNKNOWN"


class CandidateObservation(ACPIABaseModel):
    """Normalized observation schema extracted from any source agent result."""
    candidate_id: str
    observation_type: CorrelationType
    originating_agent: str
    evidence_id: str
    raw_value: str
    normalized_value: str
    confidence: float
    timestamp: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    entity_id: Optional[str] = None
    graph_node_id: Optional[str] = None
    timeline_event_id: Optional[str] = None
    source_reference: SourceReference


class CorrelationObservation(ACPIABaseModel):
    """Traceable observation detail block."""
    observation_id: str
    evidence_id: str
    originating_agent: str
    raw_value: str
    normalized_value: str
    confidence: float
    source_reference: SourceReference


class CorrelationEvidence(ACPIABaseModel):
    """Evidence link mapping."""
    evidence_id: str
    evidence_type: str
    file_name: str
    source_reference: SourceReference


class CorrelationConfidenceBreakdown(ACPIABaseModel):
    """Weighted granular scores breakdown."""
    entity_score: float
    temporal_score: float
    location_score: float
    graph_score: float
    content_score: float
    final_confidence: float


class CorrelationMatch(ACPIABaseModel):
    """A match connection linking observations across files."""
    match_id: str
    correlation_type: CorrelationType
    correlation_strength: CorrelationStrength
    confidence: float
    matching_algorithm: str
    matched_fields: List[str] = Field(default_factory=list, description="Fields causing the match")
    supporting_observations: List[CorrelationObservation] = Field(default_factory=list)
    supporting_evidence: List[CorrelationEvidence] = Field(default_factory=list)


class CorrelatedEntity(ACPIABaseModel):
    """Canonical entity reference."""
    entity_id: str
    canonical_name: str
    entity_type: str
    confidence: float


class CorrelationCluster(ACPIABaseModel):
    """Cluster of matching correlation results."""
    cluster_id: str
    cluster_name: str
    matched_entities: List[CorrelatedEntity] = Field(default_factory=list)
    matched_evidence: List[str] = Field(default_factory=list, description="Evidence IDs")
    timeline_events: List[str] = Field(default_factory=list, description="Timeline Event IDs")
    graph_nodes: List[str] = Field(default_factory=list, description="Graph Node IDs")
    graph_edges: List[str] = Field(default_factory=list, description="Graph Edge IDs")
    correlations: List[CorrelationMatch] = Field(default_factory=list)
    source_references: List[SourceReference] = Field(default_factory=list)
    cluster_primary_timestamp: Optional[datetime] = None
    confidence: float


class CorrelationConflict(ACPIABaseModel):
    """Identified contradictory records."""
    conflict_id: str
    conflict_type: ConflictType
    description: str
    conflicting_observations: List[CorrelationObservation] = Field(default_factory=list)
    confidence: float


class CorrelationStatistics(ACPIABaseModel):
    """Logical statistics counter."""
    total_candidates: int
    total_correlations: int
    total_clusters: int
    total_conflicts: int


class CorrelationValidation(ACPIABaseModel):
    """Diagnostic validation checks list."""
    integrity_status: str = "PASS"
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ProcessorExecution(ACPIABaseModel):
    """Logs per submodule run."""
    processor_name: str
    processor_version: str
    execution_time_ms: float
    status: str


class CorrelationMetrics(ACPIABaseModel):
    """Execution timing profile."""
    processing_time_ms: float
    extraction_time_ms: float
    comparison_time_ms: float
    clustering_time_ms: float
    validation_time_ms: float
    executions: List[ProcessorExecution] = Field(default_factory=list)


class CorrelationSummary(ACPIABaseModel):
    """Summary counts block."""
    correlation_distribution: Dict[str, int] = Field(default_factory=dict)
    cluster_distribution: Dict[str, int] = Field(default_factory=dict)
    average_confidence: float


class CorrelationPackage(ACPIABaseModel):
    """Root standardized cross-evidence correlation payload schema."""
    schema_version: str = "1.0.0"
    correlation_id: str
    case_id: str
    created_at: datetime
    clusters: List[CorrelationCluster] = Field(default_factory=list)
    cluster_index: Dict[str, int] = Field(default_factory=dict, description="Maps cluster_id to array index")
    conflicts: List[CorrelationConflict] = Field(default_factory=list)
    statistics: CorrelationStatistics
    validation: CorrelationValidation
    metrics: CorrelationMetrics
    summary: CorrelationSummary
