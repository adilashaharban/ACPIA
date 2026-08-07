# -*- coding: utf-8 -*-
"""Unit and integration tests for CrossEvidenceCorrelationAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.cross_evidence_correlation.agent import CrossEvidenceCorrelationAgent

def test_agent_run_success(
    metadata_result_contract: AgentResultContract,
    document_result_contract: AgentResultContract,
    vision_result_contract: AgentResultContract,
    audio_result_contract: AgentResultContract,
    entity_result_contract: AgentResultContract,
    graph_result_contract: AgentResultContract,
    timeline_result_contract: AgentResultContract
) -> None:
    """Verifies that the correlation agent run completes with a SUCCESS status wrapper."""
    agent = CrossEvidenceCorrelationAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-CR-1",
        pipeline_stage="timeline_intelligence"
    )
    
    result = agent.run(
        context=context,
        metadata_result=metadata_result_contract,
        document_result=document_result_contract,
        vision_result=vision_result_contract,
        audio_result=audio_result_contract,
        entity_result=entity_result_contract,
        graph_result=graph_result_contract,
        timeline_result=timeline_result_contract
    )
    
    assert result.agent == "cross_evidence_correlation_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "cross_evidence_correlation"
    assert len(result.errors) == 0
    assert result.payload["statistics"]["total_candidates"] > 0

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = CrossEvidenceCorrelationAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    result = agent.run(context=context, metadata_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies health check dict format."""
    agent = CrossEvidenceCorrelationAgent()
    health = agent.health()
    assert health["agent"] == "Cross-Evidence Correlation Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = CrossEvidenceCorrelationAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "cross_evidence_correlation_agent"
    assert "connected_components_clustering" in manifest.capabilities
