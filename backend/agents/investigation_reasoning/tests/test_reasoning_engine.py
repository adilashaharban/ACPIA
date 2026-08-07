# -*- coding: utf-8 -*-
"""Unit tests for ReasoningEngine."""

from backend.agents.investigation_reasoning.dispatcher import Dispatcher
from backend.agents.investigation_reasoning.reasoning_engine import ReasoningEngine

def test_reasoning_engine_loop() -> None:
    """Verifies that the structured JSON execution loop completes successfully."""
    engine = ReasoningEngine(Dispatcher())
    data, meta = engine.execute_reasoning_loop(
        prompt="Sample text query instructions",
        provider_type="gemini",
        model_name="gemini-1.5-pro",
        temperature=0.0,
        max_tokens=100
    )
    
    assert "findings" in data
    assert meta.provider == "gemini"
