# -*- coding: utf-8 -*-
"""Pydantic V2 schema definitions for the Investigation Reasoning Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, SourceReference

class InvestigationMode(str, Enum):
    """Execution mode types for user requests."""
    QUESTION_ANSWERING = "QUESTION_ANSWERING"
    SUMMARY = "SUMMARY"
    TIMELINE_ANALYSIS = "TIMELINE_ANALYSIS"
    ENTITY_ANALYSIS = "ENTITY_ANALYSIS"
    CORRELATION_ANALYSIS = "CORRELATION_ANALYSIS"
    CONTRADICTION_ANALYSIS = "CONTRADICTION_ANALYSIS"
    CUSTOM = "CUSTOM"


class InvestigationRequest(ACPIABaseModel):
    """Request query payload parameter specs."""
    request_id: str
    case_id: str
    user_query: str
    retrieval_id: str
    mode: InvestigationMode
    max_findings: int = 10
    include_reasoning_trace: bool = True


class SeverityLevel(str, Enum):
    """Categorized severity level classifications."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingType(str, Enum):
    """Factual finding categories."""
    CORRELATION = "CORRELATION"
    INCONSISTENCY = "INCONSISTENCY"
    TIMELINE_GAP = "TIMELINE_GAP"
    FACTUAL_OBSERVATION = "FACTUAL_OBSERVATION"
    CONCLUSION = "CONCLUSION"


class FindingStatus(str, Enum):
    """Validation backing status indicators."""
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONTRADICTED = "CONTRADICTED"


class FindingCitation(ACPIABaseModel):
    """Verifiable mapping citations."""
    evidence_id: str
    source_reference: SourceReference
    chunk_id: str
    retrieval_rank: int


class ReasoningConfidence(ACPIABaseModel):
    """Explainable granular confidence scoring metrics."""
    evidence_score: float
    retrieval_score: float
    citation_score: float
    consistency_score: float
    model_score: float
    final_score: float


class ReasoningStep(ACPIABaseModel):
    """Auditable reasoning execution trace."""
    step_id: str
    step_type: str
    description: str
    input_references: List[str] = Field(default_factory=list)
    output_references: List[str] = Field(default_factory=list)
    confidence: float


class Finding(ACPIABaseModel):
    """A single factual reasoning output finding."""
    finding_id: str
    title: str
    description: str
    finding_type: FindingType
    finding_status: FindingStatus
    confidence: ReasoningConfidence
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    supporting_entities: List[str] = Field(default_factory=list)
    supporting_graph_nodes: List[str] = Field(default_factory=list)
    supporting_graph_edges: List[str] = Field(default_factory=list)
    supporting_timeline_events: List[str] = Field(default_factory=list)
    supporting_correlation_clusters: List[str] = Field(default_factory=list)
    citations: List[FindingCitation] = Field(default_factory=list)
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)


class Contradiction(ACPIABaseModel):
    """Factual contradiction warning detail."""
    contradiction_id: str
    description: str
    conflicting_finding_ids: List[str] = Field(default_factory=list)
    severity: SeverityLevel = SeverityLevel.HIGH


class EvidenceGap(ACPIABaseModel):
    """Factual evidence gap details."""
    gap_id: str
    description: str
    unresolved_entities: List[str] = Field(default_factory=list)
    missing_evidence_type: str


class ReasoningTrace(ACPIABaseModel):
    """Execution traces collection."""
    trace_id: str
    steps: List[ReasoningStep] = Field(default_factory=list)


class ReasoningStatistics(ACPIABaseModel):
    """Total finding statistic counters."""
    total_findings: int
    total_contradictions: int
    total_gaps: int


class ReasoningValidation(ACPIABaseModel):
    """Diagnostic validation checks list."""
    integrity_status: str = "PASS"
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ProviderResponseMetadata(ACPIABaseModel):
    """Token usage and configuration stats."""
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    latency: float
    provider: str
    temperature: float
    seed: int
    finish_reason: str


class ProcessorExecution(ACPIABaseModel):
    """Execution log for internal modules."""
    processor_name: str
    processor_version: str
    execution_time_ms: float
    status: str


class ReasoningMetrics(ACPIABaseModel):
    """Timing and latency stats."""
    processing_time_ms: float
    prompt_time_ms: float
    parsing_time_ms: float
    validation_time_ms: float
    provider_metadata: Optional[ProviderResponseMetadata] = None
    executions: List[ProcessorExecution] = Field(default_factory=list)


class ReasoningSummary(ACPIABaseModel):
    """Summary counts block."""
    average_confidence: float
    finding_types_distribution: Dict[str, int] = Field(default_factory=dict)


class ReasoningPackage(ACPIABaseModel):
    """Root standardized investigation reasoning payload schema."""
    schema_version: str = "1.0.0"
    reasoning_id: str
    case_id: str
    retrieval_id: str
    created_at: datetime
    prompt_version: str = "v1"
    model_name: str
    model_version: str
    findings: List[Finding] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    evidence_gaps: List[EvidenceGap] = Field(default_factory=list)
    reasoning_trace: ReasoningTrace
    statistics: ReasoningStatistics
    validation: ReasoningValidation
    metrics: ReasoningMetrics
    summary: ReasoningSummary
    prompt_version: str = "v1"
