# -*- coding: utf-8 -*-
"""Unit and integration tests for DocumentIntelligenceAgent."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.document_intelligence.agent import DocumentIntelligenceAgent

def test_agent_run_success(metadata_result_contract: AgentResultContract) -> None:
    """Verifies that the document agent run completes with a SUCCESS status wrapper."""
    agent = DocumentIntelligenceAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-DOC-100",
        pipeline_stage="metadata"
    )
    
    result = agent.run(
        context=context,
        metadata_result=metadata_result_contract
    )
    
    # Assert successful wrapper layout
    assert result.agent == "document_intelligence_agent"
    assert result.status == "SUCCESS"
    assert result.processing_context.pipeline_stage == "document_intelligence"
    assert len(result.errors) == 0
    assert result.payload["summary"]["mime_type"] == "text/plain"
    assert result.payload["metrics"]["parser_used"] == "TXTParser"

def test_agent_run_validation_failure() -> None:
    """Verifies that invalid params results in FAILURE wrapper without crashes."""
    agent = DocumentIntelligenceAgent()
    context = ProcessingContextContract(case_id="C1", pipeline_stage="x")
    
    # Passing None triggers status FAILURE
    result = agent.run(context=context, metadata_result=None)
    assert result.status == "FAILURE"
    assert len(result.errors) == 1

def test_agent_health_check() -> None:
    """Verifies format of health check dict."""
    agent = DocumentIntelligenceAgent()
    health = agent.health()
    assert health["agent"] == "Document Intelligence Agent"
    assert health["status"] == "healthy"

def test_agent_manifest() -> None:
    """Verifies format of the discovery manifest."""
    agent = DocumentIntelligenceAgent()
    manifest = agent.manifest()
    assert manifest.metadata.name == "document_intelligence_agent"
    assert "pdf_structural_parsing" in manifest.capabilities
