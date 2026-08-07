# -*- coding: utf-8 -*-
"""Unit and integration tests for RAGAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.rag.agent import RAGAgent
from backend.agents.rag.schema import RetrievalRequest, RetrievalMode, RAGOperation

def test_agent_run_success(
    metadata_result_contract: AgentResultContract,
    document_result_contract: AgentResultContract,
    vision_result_contract: AgentResultContract,
    audio_result_contract: AgentResultContract,
    entity_result_contract: AgentResultContract,
    graph_result_contract: AgentResultContract,
    timeline_result_contract: AgentResultContract,
    correlation_result_contract: AgentResultContract
) -> None:
    """Verifies that the RAG agent run completes with a SUCCESS status wrapper in INDEX & RETRIEVE mode."""
    agent = RAGAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-RAG-1",
        pipeline_stage="timeline"
    )
    
    # Run INDEX
    req_idx = RetrievalRequest(
        request_id="REQ-1",
        query="",
        retrieval_mode=RetrievalMode.HYBRID,
        operation=RAGOperation.INDEX
    )
    
    result_idx = agent.run(
        context=context,
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
    
    assert result_idx.status == "SUCCESS"
    assert result_idx.payload["statistics"]["indexed_chunks"] > 0
    
    # Run RETRIEVE
    req_ret = RetrievalRequest(
        request_id="REQ-2",
        query="timestamp",
        retrieval_mode=RetrievalMode.HYBRID,
        operation=RAGOperation.RETRIEVE,
        top_k=2
    )
    
    result_ret = agent.run(
        context=context,
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
    
    assert result_ret.status == "SUCCESS"
    assert len(result_ret.payload["retrieved_chunks"]) > 0

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = RAGAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    result = agent.run(context=context, metadata_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies health check dict format."""
    agent = RAGAgent()
    health = agent.health()
    assert health["agent"] == "Retrieval-Augmented Generation Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = RAGAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "rag_agent"
    assert "dense_vector_search" in manifest.capabilities
