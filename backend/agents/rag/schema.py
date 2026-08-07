# -*- coding: utf-8 -*-
"""Pydantic V2 schema definitions for the Retrieval-Augmented Generation Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, SourceReference

class RetrievalMode(str, Enum):
    """Supported retrieval execution modes."""
    SEMANTIC = "SEMANTIC"
    KEYWORD = "KEYWORD"
    HYBRID = "HYBRID"


class ChunkType(str, Enum):
    """Categorized chunk source types."""
    DOCUMENT = "DOCUMENT"
    AUDIO = "AUDIO"
    IMAGE = "IMAGE"
    TIMELINE = "TIMELINE"
    GRAPH = "GRAPH"
    ENTITY = "ENTITY"
    CORRELATION = "CORRELATION"


class RAGOperation(str, Enum):
    """Indexing or query execution types."""
    INDEX = "INDEX"
    RETRIEVE = "RETRIEVE"
    REINDEX = "REINDEX"


class RetrievalFilter(ACPIABaseModel):
    """Structured filtering parameters for query operations."""
    case_id: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    entity_ids: List[str] = Field(default_factory=list)
    modalities: List[ChunkType] = Field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class RetrievalSource(ACPIABaseModel):
    """Structured provenance mapping which links retrieved chunks to entities and clusters."""
    agent_name: str
    package_version: str
    evidence_id: str
    case_id: Optional[str] = None
    entity_ids: List[str] = Field(default_factory=list)
    timeline_event_ids: List[str] = Field(default_factory=list)
    graph_node_ids: List[str] = Field(default_factory=list)
    graph_edge_ids: List[str] = Field(default_factory=list)
    correlation_cluster_ids: List[str] = Field(default_factory=list)
    source_reference: SourceReference


class EmbeddingInformation(ACPIABaseModel):
    """Embedding model metadata details."""
    model_name: str
    model_version: str
    embedding_dimension: int
    created_at: datetime


class RetrievalChunk(ACPIABaseModel):
    """Normalized chunks representation."""
    chunk_id: str
    evidence_id: str
    chunk_type: ChunkType
    text: str
    embedding_id: str
    embedding: EmbeddingInformation
    token_count: int
    parent_chunk_id: Optional[str] = None
    previous_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    source: RetrievalSource


class RetrievalScore(ACPIABaseModel):
    """Detailed fusion retrieval scoring metrics."""
    semantic_score: float
    keyword_score: float
    fused_score: float


class RetrievedChunk(ACPIABaseModel):
    """Search matches output chunk wraps."""
    chunk: RetrievalChunk
    score: RetrievalScore
    rank: int


class RetrievalRequest(ACPIABaseModel):
    """Retrieval query request details."""
    request_id: str
    query: str
    retrieval_mode: RetrievalMode
    operation: RAGOperation = RAGOperation.RETRIEVE
    top_k: int = 10
    filters: Optional[RetrievalFilter] = None


class RetrievalContext(ACPIABaseModel):
    """Consolidated semantic context ready for LLM consumption."""
    total_tokens: int
    context_text: str
    evidence_ids: List[str] = Field(default_factory=list)
    entity_ids: List[str] = Field(default_factory=list)
    timeline_event_ids: List[str] = Field(default_factory=list)
    graph_node_ids: List[str] = Field(default_factory=list)
    graph_edge_ids: List[str] = Field(default_factory=list)
    correlation_cluster_ids: List[str] = Field(default_factory=list)


class RetrievalStatistics(ACPIABaseModel):
    """Retrieval counter statistics."""
    indexed_chunks: int
    retrieved_chunks: int
    average_similarity: float


class RetrievalValidation(ACPIABaseModel):
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


class RetrievalMetrics(ACPIABaseModel):
    """Execution timing profile."""
    processing_time_ms: float
    indexing_time_ms: float
    embedding_time_ms: float
    retrieval_time_ms: float
    executions: List[ProcessorExecution] = Field(default_factory=list)


class RetrievalSummary(ACPIABaseModel):
    """Summary counts block."""
    total_chunks: int
    indexed_documents: int
    indexed_modalities: Dict[str, int] = Field(default_factory=dict)


class RetrievalPackage(ACPIABaseModel):
    """Root standardized retrieval package payload schema."""
    schema_version: str = "1.0.0"
    retrieval_id: str
    created_at: datetime
    query: RetrievalRequest
    context: Optional[RetrievalContext] = None
    retrieved_chunks: List[RetrievedChunk] = Field(default_factory=list)
    statistics: RetrievalStatistics
    validation: RetrievalValidation
    metrics: RetrievalMetrics
    summary: RetrievalSummary
