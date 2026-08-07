# -*- coding: utf-8 -*-
"""Unit tests for MetricsCalculator."""

from backend.agents.cross_evidence_correlation.metrics import MetricsCalculator

def test_metrics_calculator() -> None:
    """Verifies that sub-operation timings aggregate correctly."""
    metrics = MetricsCalculator.calculate(
        processing_time_ms=100.0,
        extraction_time_ms=30.0,
        comparison_time_ms=40.0,
        clustering_time_ms=20.0,
        validation_time_ms=10.0,
        executions=[]
    )
    
    assert metrics.processing_time_ms == 100.0
    assert metrics.extraction_time_ms == 30.0
    assert metrics.comparison_time_ms == 40.0
