# -*- coding: utf-8 -*-
"""Unit tests for MetricsCalculator."""

from backend.agents.investigation_reasoning.metrics import MetricsCalculator

def test_metrics_calculator() -> None:
    """Verifies that sub-operation timings aggregate correctly."""
    metrics = MetricsCalculator.calculate(
        processing_time_ms=100.0,
        prompt_time_ms=30.0,
        parsing_time_ms=40.0,
        validation_time_ms=20.0,
        provider_metadata=None,
        executions=[]
    )
    
    assert metrics.processing_time_ms == 100.0
    assert metrics.prompt_time_ms == 30.0
    assert metrics.parsing_time_ms == 40.0
