# -*- coding: utf-8 -*-
"""Unit and integration tests for KnowledgeGraphAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.knowledge_graph.agent import KnowledgeGraphAgent

def test_agent_run_success(
    metadata_result_contract: AgentResultContract,
    entity_resolution_result_contract: AgentResultContract
) -> None:
    """Verifies that the knowledge graph agent run completes with a SUCCESS status wrapper."""
    agent = KnowledgeGraphAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-KG-1",
        pipeline_stage="entity_resolution"
    )
    
    result = agent.run(
        context=context,
        metadata_result=metadata_result_contract,
        entity_result=entity_resolution_result_contract
    )
    
    assert result.agent == "knowledge_graph_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "knowledge_graph"
    assert len(result.errors) == 0
    assert len(result.payload["nodes"]) == 2
    assert len(result.payload["edges"]) == 1

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = KnowledgeGraphAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    result = agent.run(context=context, metadata_result=None, entity_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies health check dict format."""
    agent = KnowledgeGraphAgent()
    health = agent.health()
    assert health["agent"] == "Knowledge Graph Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = KnowledgeGraphAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "knowledge_graph_agent"
    assert "node_builder_mapping" in manifest.capabilities
