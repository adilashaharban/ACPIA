# -*- coding: utf-8 -*-
"""Pydantic V2 schema definitions for the Knowledge Graph Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Union, Any
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, SourceReference

class NodeType(str, Enum):
    """Supported node categories in the investigation graph."""
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
    EVENT = "EVENT"
    LOCATION = "LOCATION"
    UNKNOWN = "UNKNOWN"


class EdgeType(str, Enum):
    """Supported edge relationship types between investigation nodes."""
    OWNS = "OWNS"
    USES = "USES"
    COMMUNICATED_WITH = "COMMUNICATED_WITH"
    APPEARS_IN = "APPEARS_IN"
    MENTIONED_IN = "MENTIONED_IN"
    OBSERVED_IN = "OBSERVED_IN"
    LOCATED_AT = "LOCATED_AT"
    CREATED = "CREATED"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    CONTAINS = "CONTAINS"
    CAPTURED_BY = "CAPTURED_BY"
    RECORDED_BY = "RECORDED_BY"
    ATTACHED_TO = "ATTACHED_TO"
    REFERENCES = "REFERENCES"
    SAME_AS = "SAME_AS"
    LINKED_TO = "LINKED_TO"


class EdgeDirection(str, Enum):
    """Specifies directional constraints on entity links."""
    DIRECTED = "DIRECTED"
    UNDIRECTED = "UNDIRECTED"


class GraphProperty(ACPIABaseModel):
    """Traceable, explainable property representation, restricted to clean primitive types."""
    key: str
    value: Union[str, int, float, bool]
    confidence: float
    source_reference: SourceReference


class GraphObservation(ACPIABaseModel):
    """Traceable observation record."""
    observation_id: str
    evidence_id: str
    raw_value: str
    confidence: float
    source_reference: SourceReference


class GraphEvidenceReference(ACPIABaseModel):
    """Evidence metadata reference."""
    evidence_id: str
    source_reference: SourceReference


class GraphNode(ACPIABaseModel):
    """Investigation graph node."""
    node_id: str
    entity_id: str
    node_type: NodeType
    label: str
    properties: List[GraphProperty] = Field(default_factory=list)
    confidence: float
    source_references: List[SourceReference] = Field(default_factory=list)
    supporting_observations: List[GraphObservation] = Field(default_factory=list)


class GraphEdge(ACPIABaseModel):
    """Standardized relationship link between graph nodes."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: EdgeType
    direction: EdgeDirection
    confidence: float
    supporting_evidence: List[GraphEvidenceReference] = Field(default_factory=list)
    supporting_observations: List[GraphObservation] = Field(default_factory=list)
    creation_method: str = Field(default="DETERMINISTIC_EXTRACTION")
    graph_version: str = Field(default="1.0.0")


class GraphStatistics(ACPIABaseModel):
    """Calculated graph topological stats."""
    node_count: int
    edge_count: int
    isolated_node_count: int
    density: float


class GraphValidation(ACPIABaseModel):
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


class GraphMetrics(ACPIABaseModel):
    """Execution timing profile."""
    processing_time_ms: float
    node_build_time_ms: float
    edge_build_time_ms: float
    validation_time_ms: float
    repository_time_ms: float
    executions: List[ProcessorExecution] = Field(default_factory=list)


class GraphSummary(ACPIABaseModel):
    """Logical metrics counters."""
    node_distribution: Dict[str, int] = Field(default_factory=dict)
    edge_distribution: Dict[str, int] = Field(default_factory=dict)


class KnowledgeGraphPackage(ACPIABaseModel):
    """Root standardized investigation graph package payload schema."""
    schema_version: str = "1.0.0"
    graph_id: str
    case_id: str
    created_at: datetime
    graph_version: str = "1.0.0"
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    statistics: GraphStatistics
    validation: GraphValidation
    metrics: GraphMetrics
    summary: GraphSummary
