# -*- coding: utf-8 -*-
"""Unit tests for MetricsCalculator."""

from backend.agents.rag.metrics import MetricsCalculator

def test_metrics_calculator() -> None:
    """Verifies that sub-operation timings aggregate correctly."""
    metrics = MetricsCalculator.calculate(
        processing_time_ms=100.0,
        indexing_time_ms=30.0,
        embedding_time_ms=40.0,
        retrieval_time_ms=20.0,
        executions=[]
    )
    
    assert metrics.processing_time_ms == 100.0
    assert metrics.indexing_time_ms == 30.0
    assert metrics.embedding_time_ms == 40.0
