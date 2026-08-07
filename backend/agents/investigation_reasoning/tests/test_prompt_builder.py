# -*- coding: utf-8 -*-
"""Unit tests for PromptBuilder."""

from backend.agents.investigation_reasoning.prompt_builder import PromptBuilder
from backend.agents.investigation_reasoning.schema import InvestigationRequest, InvestigationMode

def test_prompt_builder(mock_investigation_request: InvestigationRequest) -> None:
    """Verifies prompt strings are assembled cleanly from templates."""
    builder = PromptBuilder()
    prompt = builder.build_prompt(
        request=mock_investigation_request,
        context_text="Sample RAG context details",
        entities_summary="Entities summary list"
    )
    
    assert "Who is the suspect?" in prompt
    assert "Sample RAG context details" in prompt
