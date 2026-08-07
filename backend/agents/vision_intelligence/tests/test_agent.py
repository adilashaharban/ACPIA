# -*- coding: utf-8 -*-
"""Unit and integration tests for VisionIntelligenceAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.vision_intelligence.agent import VisionIntelligenceAgent

def test_agent_run_success(metadata_result_contract: AgentResultContract) -> None:
    """Verifies that the vision agent run completes with a SUCCESS status wrapper."""
    agent = VisionIntelligenceAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-VIS-99",
        pipeline_stage="metadata"
    )
    
    result = agent.run(
        context=context,
        metadata_result=metadata_result_contract
    )
    
    assert result.agent == "vision_intelligence_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "vision_intelligence"
    assert len(result.errors) == 0
    assert result.payload["summary"]["mime_type"] == "image/jpeg"
    assert len(result.payload["objects"]) == 1

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = VisionIntelligenceAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    result = agent.run(context=context, metadata_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies health check dict format."""
    agent = VisionIntelligenceAgent()
    health = agent.health()
    assert health["agent"] == "Vision Intelligence Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = VisionIntelligenceAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "vision_intelligence_agent"
    assert "object_detection_cv" in manifest.capabilities
