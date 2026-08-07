# -*- coding: utf-8 -*-
"""Unit and integration tests for InvestigationReasoningAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.investigation_reasoning.agent import InvestigationReasoningAgent
from backend.agents.investigation_reasoning.schema import InvestigationRequest
from backend.agents.rag.schema import RetrievalPackage

def test_agent_run_success(
    metadata_result_contract: AgentResultContract,
    mock_retrieval_package: RetrievalPackage,
    mock_investigation_request: InvestigationRequest
) -> None:
    """Verifies that the reasoning agent run completes with a SUCCESS status wrapper."""
    agent = InvestigationReasoningAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-REAS-1",
        pipeline_stage="timeline"
    )
    
    result = agent.run(
        context=context,
        request=mock_investigation_request,
        retrieval_pkg=mock_retrieval_package,
        metadata_result=metadata_result_contract
    )
    
    assert result.agent == "investigation_reasoning_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "investigation_reasoning"
    assert len(result.errors) == 0
    assert len(result.payload["findings"]) > 0

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = InvestigationReasoningAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    result = agent.run(context=context, metadata_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies health check dict format."""
    agent = InvestigationReasoningAgent()
    health = agent.health()
    assert health["agent"] == "Investigation Reasoning Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = InvestigationReasoningAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "investigation_reasoning_agent"
    assert "structured_findings" in manifest.capabilities
