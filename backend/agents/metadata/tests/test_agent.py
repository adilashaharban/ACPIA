# -*- coding: utf-8 -*-
"""Unit and integration tests for MetadataAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.metadata.agent import MetadataAgent

def test_agent_run_success(intake_result_contract: AgentResultContract) -> None:
    """Verifies that the metadata agent run completes with a SUCCESS status wrapper."""
    agent = MetadataAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-TEST-100",
        pipeline_stage="evidence_intake"
    )
    
    result = agent.run(
        context=context,
        intake_result=intake_result_contract
    )
    
    # Assert successful wrapper layout
    assert result.agent == "metadata_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "metadata"
    assert len(result.errors) == 0
    assert result.payload["summary"]["file_type_category"] == "image"
    assert result.payload["metrics"]["extractor_used"] == "ImageExtractor"

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = MetadataAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    # Passing None triggers status FAILURE
    result = agent.run(context=context, intake_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies format of health check dict."""
    agent = MetadataAgent()
    health = agent.health()
    assert health["agent"] == "Metadata Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = MetadataAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "metadata_agent"
    assert "exif_decoding" in manifest.capabilities
