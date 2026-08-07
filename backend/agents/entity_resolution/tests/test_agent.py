# -*- coding: utf-8 -*-
"""Unit and integration tests for EntityResolutionAgent."""

from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.entity_resolution.agent import EntityResolutionAgent

def test_agent_run_success(
    metadata_result_contract: AgentResultContract,
    document_result_contract: AgentResultContract,
    vision_result_contract: AgentResultContract,
    audio_result_contract: AgentResultContract
) -> None:
    """Verifies that the entity resolution agent run completes with a SUCCESS status wrapper."""
    agent = EntityResolutionAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-ENT-1",
        pipeline_stage="metadata"
    )
    
    result = agent.run(
        context=context,
        metadata_result=metadata_result_contract,
        document_result=document_result_contract,
        vision_result=vision_result_contract,
        audio_result=audio_result_contract
    )
    
    assert result.agent == "entity_resolution_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "entity_resolution"
    assert len(result.errors) == 0
    assert len(result.payload["entities"]) > 0

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = EntityResolutionAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    result = agent.run(context=context, metadata_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies health check dict format."""
    agent = EntityResolutionAgent()
    health = agent.health()
    assert health["agent"] == "Entity Resolution Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = EntityResolutionAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "entity_resolution_agent"
    assert "entity_normalization_e164" in manifest.capabilities
