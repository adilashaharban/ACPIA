# -*- coding: utf-8 -*-
"""Pydantic V2 schema definitions for the Entity Resolution Agent."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, SourceReference

class EntityType(str, Enum):
    """Supported entity categories across modal formats."""
    PERSON = "PERSON"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    ADDRESS = "ADDRESS"
    DEVICE = "DEVICE"
    IMEI = "IMEI"
    IMSI = "IMSI"
    VEHICLE = "VEHICLE"
    PLATE = "PLATE"
    ORGANIZATION = "ORGANIZATION"
    WEBSITE = "WEBSITE"
    URL = "URL"
    SOCIAL_ACCOUNT = "SOCIAL_ACCOUNT"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    UPI = "UPI"
    PASSPORT = "PASSPORT"
    GOVERNMENT_ID = "GOVERNMENT_ID"
    IP_ADDRESS = "IP_ADDRESS"
    MAC_ADDRESS = "MAC_ADDRESS"
    CRYPTO_WALLET = "CRYPTO_WALLET"
    FILE = "FILE"
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    UNKNOWN = "UNKNOWN"


class ResolutionMethod(str, Enum):
    """Matching execution types."""
    EXACT_MATCH = "EXACT_MATCH"
    NORMALIZED_MATCH = "NORMALIZED_MATCH"
    FUZZY_MATCH = "FUZZY_MATCH"
    CROSS_MODAL_MATCH = "CROSS_MODAL_MATCH"
    MANUAL = "MANUAL"


class RelationshipType(str, Enum):
    """Enums representing visual relationship tags."""
    OWNER_OF = "OWNER_OF"
    USES = "USES"
    MENTIONED_WITH = "MENTIONED_WITH"
    OBSERVED_WITH = "OBSERVED_WITH"
    RECORDED_IN = "RECORDED_IN"
    APPEARS_IN = "APPEARS_IN"
    UNKNOWN = "UNKNOWN"


class MatchingAlgorithm(str, Enum):
    """Specific matching algorithm engines."""
    EXACT = "EXACT"
    LEVENSHTEIN = "LEVENSHTEIN"
    JARO_WINKLER = "JARO_WINKLER"
    TOKEN_SET_RATIO = "TOKEN_SET_RATIO"
    CROSS_MODAL = "CROSS_MODAL"


class EntityAlias(ACPIABaseModel):
    """Alias mappings."""
    alias_name: str
    confidence: float
    source_reference: SourceReference


class EntityAttribute(ACPIABaseModel):
    """Attribute details."""
    key: str
    value: str
    confidence: float
    source_reference: SourceReference


class EntityObservation(ACPIABaseModel):
    """Traceable observation record."""
    observation_id: str
    evidence_id: str
    entity_type: EntityType
    raw_value: str
    normalized_value: str
    confidence: float
    source_reference: SourceReference


class CandidateEntity(ACPIABaseModel):
    """Standardized intermediate candidate representation pooled from extractors."""
    candidate_id: str
    entity_type: EntityType
    raw_value: str
    normalized_value: str
    confidence: float
    extraction_agent: str
    source_reference: SourceReference
    supporting_attributes: List[EntityAttribute] = Field(default_factory=list)


class MatchingEvidence(ACPIABaseModel):
    """Explainable linkage record between candidate and canonical entity."""
    observation_id: str
    algorithm: MatchingAlgorithm
    similarity_score: float
    matched_fields: List[str] = Field(default_factory=list)


class EntityRelationshipReference(ACPIABaseModel):
    """Graph linking target enums."""
    target_entity_id: str
    relationship_type: RelationshipType
    confidence: float
    source_reference: SourceReference


class ConfidenceBreakdown(ACPIABaseModel):
    """Explainable breakdown of final confidence computation."""
    exact_match_score: float
    fuzzy_match_score: float
    cross_modal_score: float
    evidence_count_score: float
    final_confidence: float


class CanonicalEntity(ACPIABaseModel):
    """Deduplicated canonical entity record."""
    entity_id: str
    entity_type: EntityType
    canonical_name: str
    aliases: List[EntityAlias] = Field(default_factory=list)
    attributes: List[EntityAttribute] = Field(default_factory=list)
    confidence_breakdown: ConfidenceBreakdown
    source_references: List[SourceReference] = Field(default_factory=list)
    supporting_observations: List[EntityObservation] = Field(default_factory=list)
    linked_evidence: List[str] = Field(default_factory=list, description="Evidence ID list")
    creation_method: ResolutionMethod
    resolution_version: str = Field(default="1.0.0")


class ResolvedEntity(ACPIABaseModel):
    """Logical mapping wrapper."""
    canonical: CanonicalEntity
    matches: List[MatchingEvidence] = Field(default_factory=list, description="Linked observations")


class EntityStatistics(ACPIABaseModel):
    """Counts of resolved items."""
    total_candidates: int
    resolved_count: int
    merged_count: int
    cluster_count: int


class EntityValidation(ACPIABaseModel):
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


class EntityMetrics(ACPIABaseModel):
    """Aggregated processing speeds and metrics."""
    processing_time_ms: float
    candidate_count: int
    normalization_count: int
    match_count: int
    merge_count: int
    executions: List[ProcessorExecution] = Field(default_factory=list)


class EntitySummary(ACPIABaseModel):
    """High level indices."""
    resolved_types: Dict[str, int] = Field(default_factory=dict)
    average_resolution_confidence: float


class EntityResolutionPackage(ACPIABaseModel):
    """Root standardized entity package payload schema."""
    schema_version: str = "1.0.0"
    entities: List[CanonicalEntity] = Field(default_factory=list)
    statistics: EntityStatistics
    validation: EntityValidation
    metrics: EntityMetrics
    summary: EntitySummary
