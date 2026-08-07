# -*- coding: utf-8 -*-
"""Unit tests for TimelineMetricsCalculator."""

from backend.agents.timeline_intelligence.metrics import TimelineMetricsCalculator
from backend.agents.timeline_intelligence.schema import ProcessorExecution

def test_metrics_calculator() -> None:
    """Verifies that sub-operation timings aggregate correctly."""
    executions = [
        ProcessorExecution(
            processor_name="TimestampNormalizer",
            processor_version="1.0.0",
            execution_time_ms=5.0,
            status="SUCCESS"
        )
    ]
    
    metrics = TimelineMetricsCalculator.calculate(
        processing_time_ms=15.0,
        timestamp_normalization_time_ms=5.0,
        merge_time_ms=2.0,
        sorting_time_ms=1.0,
        validation_time_ms=1.0,
        builder_time_ms=3.0,
        executions=executions
    )
    
    assert metrics.processing_time_ms == 15.0
    assert metrics.timestamp_normalization_time_ms == 5.0
    assert len(metrics.executions) == 1
