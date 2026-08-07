# -*- coding: utf-8 -*-
"""Retrieval-Augmented Generation Agent."""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.core.logger import get_logger
from backend.version import __version__
from backend.agents.base.base_agent import BaseAgent
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.base.agent_result import AgentResultContract
from backend.agents.base.metadata import AgentMetadata
from backend.agents.base.manifest import AgentManifest
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
from backend.agents.rag.repositories.faiss_repository import FAISSRepository
from backend.agents.rag.pipeline import RAGPipeline
from backend.agents.rag.exceptions import RAGError
from backend.agents.rag.schema import RetrievalRequest, RetrievalMode, RAGOperation

logger = get_logger("agents.rag.agent")

class RAGAgent(BaseAgent):
    """Stateless RAG agent compiling searchable hybrid indexing and contexts."""
    
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="rag_agent",
            version="1.0.0",
            description="Transforms multi-modal structured investigation outputs into searchable hybrid indices.",
            supported_input_types=["RetrievalRequest", "AgentResultContracts"],
            supported_output_types=["RetrievalPackage"],
            dependencies=["faiss", "numpy"]
        ),
        capabilities=[
            "dense_vector_search",
            "bm25_lexical_search",
            "metadata_filters",
            "context_summaries"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        dispatcher: Optional[Dispatcher] = None,
        chunk_builder: Optional[ChunkBuilder] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        keyword_index: Optional[KeywordIndex] = None,
        vector_index: Optional[VectorIndex] = None,
        hybrid_retriever: Optional[HybridRetriever] = None,
        reranker: Optional[Reranker] = None,
        context_builder: Optional[ContextBuilder] = None,
        query_expander: Optional[QueryExpander] = None,
        validator: Optional[Validator] = None,
        metrics_calculator: Optional[MetricsCalculator] = None,
        repository: Optional[SQLiteRepository] = None,
        pipeline: Optional[RAGPipeline] = None
    ) -> None:
        self.dispatcher = dispatcher or Dispatcher()
        self.chunk_builder = chunk_builder or ChunkBuilder()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.keyword_index = keyword_index or KeywordIndex()
        
        # Share the same underlying sqlite repository for index lookups
        self.repository = repository or SQLiteRepository()
        self.faiss_repo = FAISSRepository()
        
        self.vector_index = vector_index or VectorIndex(repository=self.faiss_repo)
        self.hybrid_retriever = hybrid_retriever or HybridRetriever(
            vector_index=self.vector_index,
            keyword_index=self.keyword_index
        )
        self.reranker = reranker or Reranker()
        self.context_builder = context_builder or ContextBuilder()
        self.query_expander = query_expander or QueryExpander()
        self.validator = validator or Validator()
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        
        self.pipeline = pipeline or RAGPipeline(
            dispatcher=self.dispatcher,
            chunk_builder=self.chunk_builder,
            embedding_generator=self.embedding_generator,
            keyword_index=self.keyword_index,
            vector_index=self.vector_index,
            hybrid_retriever=self.hybrid_retriever,
            reranker=self.reranker,
            context_builder=self.context_builder,
            query_expander=self.query_expander,
            validator=self.validator,
            metrics_calculator=self.metrics_calculator,
            repository=self.repository
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Executes indexing or query retrieval pipeline.
        
        Args:
            context: Active tracing context.
            **kwargs: Must contain:
                - request (RetrievalRequest): Action command request.
                - metadata_result (AgentResultContract): Metadata Agent output.
                - document_result (AgentResultContract): Optional Document Agent output.
                - vision_result (AgentResultContract): Optional Vision Agent output.
                - audio_result (AgentResultContract): Optional Audio Agent output.
                - entity_result (AgentResultContract): Optional Entity Resolution output.
                - graph_result (AgentResultContract): Optional Knowledge Graph output.
                - timeline_result (AgentResultContract): Optional Timeline output.
                - correlation_result (AgentResultContract): Optional Correlation output.
                
        Returns:
            Standardized AgentResultContract output.
        """
        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        
        status = "SUCCESS"
        payload: Dict[str, Any] = {}
        warnings: List[str] = []
        errors: List[str] = []
        
        request = kwargs.get("request")
        metadata_result = kwargs.get("metadata_result")
        document_result = kwargs.get("document_result")
        vision_result = kwargs.get("vision_result")
        audio_result = kwargs.get("audio_result")
        entity_result = kwargs.get("entity_result")
        graph_result = kwargs.get("graph_result")
        timeline_result = kwargs.get("timeline_result")
        correlation_result = kwargs.get("correlation_result")
        
        try:
            if not isinstance(request, RetrievalRequest):
                # Fallback to default INDEX request
                request = RetrievalRequest(
                    request_id="REQ-DEF-1",
                    query="default",
                    retrieval_mode=RetrievalMode.HYBRID,
                    operation=RAGOperation.INDEX
                )
                
            if not isinstance(metadata_result, AgentResultContract):
                raise ValueError("Parameter 'metadata_result' must be an AgentResultContract.")
                
            # Execute pipeline
            package, pipeline_warnings = self.pipeline.execute(
                request=request,
                metadata_result=metadata_result,
                document_result=document_result,
                vision_result=vision_result,
                audio_result=audio_result,
                entity_result=entity_result,
                graph_result=graph_result,
                timeline_result=timeline_result,
                correlation_result=correlation_result
            )
            payload = package.model_dump()
            warnings.extend(pipeline_warnings)
            
        except RAGError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain RAG execution failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside RAGAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        context.pipeline_stage = "rag"
        
        return AgentResultContract(
            agent="rag_agent",
            status=status,
            processing_context=context,
            payload=payload,
            metrics={
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "processing_time_ms": round(elapsed_ms, 2)
            },
            warnings=warnings,
            errors=errors
        )

    def health(self) -> dict:
        """Exposes health metrics and version status."""
        return {
            "agent": "Retrieval-Augmented Generation Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest capability profile."""
        return self._MANIFEST
export_agent = RAGAgent
