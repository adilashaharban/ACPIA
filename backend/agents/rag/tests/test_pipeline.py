# -*- coding: utf-8 -*-
"""Unit and integration tests for RAGPipeline."""

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
from backend.agents.rag.repositories.faiss_repository import FAISSRepository
from backend.agents.rag.pipeline import RAGPipeline
from backend.agents.rag.schema import RetrievalRequest, RetrievalMode, RAGOperation

def test_pipeline_happy_path(
    metadata_result_contract: AgentResultContract,
    document_result_contract: AgentResultContract,
    vision_result_contract: AgentResultContract,
    audio_result_contract: AgentResultContract,
    entity_result_contract: AgentResultContract,
    graph_result_contract: AgentResultContract,
    timeline_result_contract: AgentResultContract,
    correlation_result_contract: AgentResultContract
) -> None:
    """Verifies that the RAG pipeline indexes texts and executes query lookups successfully."""
    # Instantiators
    db_repo = SQLiteRepository(":memory:")
    fs_repo = FAISSRepository()
    
    kw_index = KeywordIndex()
    v_index = VectorIndex(repository=fs_repo)
    
    pipeline = RAGPipeline(
        dispatcher=Dispatcher(),
        chunk_builder=ChunkBuilder(),
        embedding_generator=EmbeddingGenerator(),
        keyword_index=kw_index,
        vector_index=v_index,
        hybrid_retriever=HybridRetriever(v_index, kw_index),
        reranker=Reranker(),
        context_builder=ContextBuilder(),
        query_expander=QueryExpander(),
        validator=Validator(),
        metrics_calculator=MetricsCalculator(),
        repository=db_repo
    )
    
    # 1. Run INDEX Mode
    req_idx = RetrievalRequest(
        request_id="REQ-1",
        query="",
        retrieval_mode=RetrievalMode.HYBRID,
        operation=RAGOperation.INDEX
    )
    
    p_idx, warnings_idx = pipeline.execute(
        request=req_idx,
        metadata_result=metadata_result_contract,
        document_result=document_result_contract,
        vision_result=vision_result_contract,
        audio_result=audio_result_contract,
        entity_result=entity_result_contract,
        graph_result=graph_result_contract,
        timeline_result=timeline_result_contract,
        correlation_result=correlation_result_contract
    )
    
    assert p_idx.statistics.indexed_chunks > 0
    
    # 2. Run RETRIEVE Mode
    req_ret = RetrievalRequest(
        request_id="REQ-2",
        query="timestamp",
        retrieval_mode=RetrievalMode.HYBRID,
        operation=RAGOperation.RETRIEVE,
        top_k=5
    )
    
    p_ret, warnings_ret = pipeline.execute(
        request=req_ret,
        metadata_result=metadata_result_contract,
        document_result=document_result_contract,
        vision_result=vision_result_contract,
        audio_result=audio_result_contract,
        entity_result=entity_result_contract,
        graph_result=graph_result_contract,
        timeline_result=timeline_result_contract,
        correlation_result=correlation_result_contract
    )
    
    assert len(p_ret.retrieved_chunks) > 0
    assert p_ret.context is not None
    assert p_ret.context.total_tokens > 0
