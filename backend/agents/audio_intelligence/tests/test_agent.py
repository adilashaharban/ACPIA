# -*- coding: utf-8 -*-
"""Unit and integration tests for AudioIntelligenceAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.audio_intelligence.agent import AudioIntelligenceAgent

def test_agent_run_success(metadata_result_contract: AgentResultContract) -> None:
    """Verifies that the audio agent run completes with a SUCCESS status wrapper."""
    agent = AudioIntelligenceAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-AUD-77",
        pipeline_stage="metadata"
    )
    
    result = agent.run(
        context=context,
        metadata_result=metadata_result_contract
    )
    
    assert result.agent == "audio_intelligence_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "audio_intelligence"
    assert len(result.errors) == 0
    assert result.payload["summary"]["mime_type"] == "audio/wav"
    assert len(result.payload["transcript"]) == 1

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = AudioIntelligenceAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    result = agent.run(context=context, metadata_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies health check dict format."""
    agent = AudioIntelligenceAgent()
    health = agent.health()
    assert health["agent"] == "Audio Intelligence Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = AudioIntelligenceAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "audio_intelligence_agent"
    assert "speech_to_text_transcription" in manifest.capabilities
