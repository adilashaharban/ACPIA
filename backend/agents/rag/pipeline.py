# -*- coding: utf-8 -*-
"""RAG pipeline orchestration."""

import time
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any, Optional
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract
from backend.agents.rag.dispatcher import Dispatcher
from backend.agents.rag.chunk_builder import ChunkBuilder
from backend.agents.rag.embedding_generator import EmbeddingGenerator
from backend.agents.rag.keyword_index import KeywordIndex
from backend.agents.rag.vector_index import VectorIndex
from backend.agents.rag.hybrid_retriever import HybridRetriever
from backend.agents.rag.reranker import Reranker
from backend.agents.rag.context_builder import ContextBuilder
from backend.agents.rag.query_expander import QueryExpander
from backend.agents.rag.validator import Validator
from backend.agents.rag.metrics import MetricsCalculator
from backend.agents.rag.repositories.sqlite_repository import SQLiteRepository
from backend.agents.rag.exceptions import RAGError
from backend.agents.rag.schema import (
    RetrievalPackage, RetrievalRequest, RetrievedChunk, RetrievalStatistics,
    RetrievalSummary, ProcessorExecution, RAGOperation
)

logger = get_logger("agents.rag.pipeline")

class RAGPipeline:
    """Orchestrates RAG indexing and retrieval execution modes."""
    
    def __init__(
        self,
        dispatcher: Dispatcher,
        chunk_builder: ChunkBuilder,
        embedding_generator: EmbeddingGenerator,
        keyword_index: KeywordIndex,
        vector_index: VectorIndex,
        hybrid_retriever: HybridRetriever,
        reranker: Reranker,
        context_builder: ContextBuilder,
        query_expander: QueryExpander,
        validator: Validator,
        metrics_calculator: MetricsCalculator,
        repository: Optional[SQLiteRepository] = None
    ) -> None:
        self.dispatcher = dispatcher
        self.chunk_builder = chunk_builder
        self.embedding_generator = embedding_generator
        self.keyword_index = keyword_index
        self.vector_index = vector_index
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker
        self.context_builder = context_builder
        self.query_expander = query_expander
        self.validator = validator
        self.metrics_calculator = metrics_calculator
        self.repository = repository or SQLiteRepository()

    def execute(
        self,
        request: RetrievalRequest,
        metadata_result: AgentResultContract,
        document_result: Optional[AgentResultContract] = None,
        vision_result: Optional[AgentResultContract] = None,
        audio_result: Optional[AgentResultContract] = None,
        entity_result: Optional[AgentResultContract] = None,
        graph_result: Optional[AgentResultContract] = None,
        timeline_result: Optional[AgentResultContract] = None,
        correlation_result: Optional[AgentResultContract] = None
    ) -> Tuple[RetrievalPackage, List[str]]:
        """Executes indexing or retrieval pipeline.
        
        Args:
            request: Action details.
            metadata_result: Metadata result wrapper.
            document_result: Optional Document result wrapper.
            ...
            
        Returns:
            Tuple containing (RetrievalPackage, warnings list).
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        executions_log: List[ProcessorExecution] = []
        
        meta_payload = metadata_result.payload
        if not meta_payload:
            raise RAGError("Input metadata payload is empty.")
            
        evidence_id = meta_payload.get("evidence_id")
        
        # 1. Fetch paths from database context
        from backend.database.session import get_db_context
        from backend.database.repositories.evidence_repository import EvidenceRepository
        
        file_path = None
        expected_hash = None
        
        with get_db_context() as db:
            repo = EvidenceRepository(db)
            db_evidence = repo.get_by_id(evidence_id)
            if not db_evidence:
                raise RAGError(f"Evidence {evidence_id} not registered in database.")
            file_path = db_evidence.file_path
            expected_hash = db_evidence.sha256_hash
            
        # 2. Checksum validation
        self.validator.verify_integrity(file_path, expected_hash)
        
        indexing_time = 0.0
        embedding_time = 0.0
        retrieval_time = 0.0
        
        retrieved_chunks: List[RetrievedChunk] = []
        context_data = None
        
        # EXECUTE OPERATION INDEX/RETRIEVE
        if request.operation == RAGOperation.INDEX or request.operation == RAGOperation.REINDEX:
            t0 = time.perf_counter()
            # Gather raw texts
            items = self.dispatcher.gather_text_items(
                metadata_payload=meta_payload,
                document_payload=document_result.payload if document_result else None,
                vision_payload=vision_result.payload if vision_result else None,
                audio_payload=audio_result.payload if audio_result else None,
                entity_payload=entity_result.payload if entity_result else None,
                graph_payload=graph_result.payload if graph_result else None,
                timeline_payload=timeline_result.payload if timeline_result else None,
                correlation_payload=correlation_result.payload if correlation_result else None,
                file_path=file_path,
                evidence_id=evidence_id
            )
            
            # Chunk builder
            dim = self.embedding_generator.get_dimension()
            chunks = self.chunk_builder.build_chunks(
                extracted_items=items,
                model_name=self.embedding_generator.provider.model_name,
                dimension=dim
            )
            indexing_time = (time.perf_counter() - t0) * 1000.0
            
            # Save chunks to vector and keyword index database
            t0 = time.perf_counter()
            self.vector_index.add_chunks(chunks)
            self.keyword_index.add_chunks(chunks)
            self.repository.add_chunks(chunks)
            embedding_time = (time.perf_counter() - t0) * 1000.0
            
            executions_log.append(
                ProcessorExecution(
                    processor_name="ChunkIndexer",
                    processor_version="1.0.0",
                    execution_time_ms=round(indexing_time + embedding_time, 2),
                    status="SUCCESS"
                )
            )
            
        elif request.operation == RAGOperation.RETRIEVE:
            t0 = time.perf_counter()
            # Query expansion
            expanded_q = self.query_expander.expand(request.query)
            
            # Embed query
            q_vector = self.embedding_generator.generate(expanded_q)
            
            # Hybrid retriever search
            candidates = self.hybrid_retriever.retrieve(
                query=expanded_q,
                query_vector=q_vector,
                retrieval_mode=request.retrieval_mode,
                top_k=request.top_k,
                filters=request.filters
            )
            
            # Re-ranker
            retrieved_chunks = self.reranker.rerank(candidates)
            retrieval_time = (time.perf_counter() - t0) * 1000.0
            
            # Context builder
            context_data = self.context_builder.build_context(retrieved_chunks)
            
            executions_log.append(
                ProcessorExecution(
                    processor_name="HybridRetriever",
                    processor_version="1.0.0",
                    execution_time_ms=round(retrieval_time, 2),
                    status="SUCCESS"
                )
            )
            
        # Run validation
        t0 = time.perf_counter()
        validation_status = self.validator.validate_package(retrieved_chunks)
        warnings.extend(validation_status.warnings)
        val_time = (time.perf_counter() - t0) * 1000.0
        
        # Aggregate statistics and summary details
        avg_sim = sum(c.score.fused_score for c in retrieved_chunks) / len(retrieved_chunks) if retrieved_chunks else 0.0
        
        stats = RetrievalStatistics(
            indexed_chunks=self.repository.count(),
            retrieved_chunks=len(retrieved_chunks),
            average_similarity=round(avg_sim, 4)
        )
        
        summary = RetrievalSummary(
            total_chunks=self.repository.count(),
            indexed_documents=self.repository.count(),
            indexed_modalities={}
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = self.metrics_calculator.calculate(
            processing_time_ms=elapsed_ms,
            indexing_time_ms=indexing_time,
            embedding_time_ms=embedding_time,
            retrieval_time_ms=retrieval_time,
            executions=executions_log
        )
        
        package = RetrievalPackage(
            schema_version="1.0.0",
            retrieval_id=f"RET-{request.request_id}",
            created_at=datetime.now(timezone.utc),
            query=request,
            context=context_data,
            retrieved_chunks=retrieved_chunks,
            statistics=stats,
            validation=validation_status,
            metrics=metrics,
            summary=summary
        )
        
        return package, warnings
export_pipeline = RAGPipeline
