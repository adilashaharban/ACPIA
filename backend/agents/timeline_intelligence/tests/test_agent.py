# -*- coding: utf-8 -*-
"""Unit and integration tests for TimelineIntelligenceAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.timeline_intelligence.agent import TimelineIntelligenceAgent

def test_agent_run_success(
    metadata_result_contract: AgentResultContract,
    document_result_contract: AgentResultContract,
    vision_result_contract: AgentResultContract,
    audio_result_contract: AgentResultContract,
    graph_result_contract: AgentResultContract
) -> None:
    """Verifies that the timeline intelligence agent run completes with a SUCCESS status wrapper."""
    agent = TimelineIntelligenceAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-TM-1",
        pipeline_stage="knowledge_graph"
    )
    
    result = agent.run(
        context=context,
        metadata_result=metadata_result_contract,
        document_result=document_result_contract,
        vision_result=vision_result_contract,
        audio_result=audio_result_contract,
        graph_result=graph_result_contract
    )
    
    assert result.agent == "timeline_intelligence_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "timeline_intelligence"
    assert len(result.errors) == 0
    # Payload has timeline package properties
    assert len(result.payload["events"]) > 0
    assert len(result.payload["event_index"]) == len(result.payload["events"])

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = TimelineIntelligenceAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    result = agent.run(context=context, metadata_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies health check dict format."""
    agent = TimelineIntelligenceAgent()
    health = agent.health()
    assert health["agent"] == "Timeline Intelligence Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = TimelineIntelligenceAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "timeline_intelligence_agent"
    assert "timestamp_normalization_utc" in manifest.capabilities
