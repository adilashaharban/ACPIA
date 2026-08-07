# -*- coding: utf-8 -*-
"""Unit tests for EntityMetricsCalculator."""

from backend.agents.entity_resolution.metrics import EntityMetricsCalculator
from backend.agents.entity_resolution.schema import ProcessorExecution

def test_metrics_calculator() -> None:
    """Verifies that stats computes correct execution values."""
    executions = [
        ProcessorExecution(
            processor_name="MetadataExtractor",
            processor_version="1.0.0",
            execution_time_ms=5.0,
            status="SUCCESS"
        )
    ]
    
    metrics = EntityMetricsCalculator.calculate(
        processing_time_ms=10.0,
        candidate_count=2,
        normalization_count=2,
        match_count=1,
        merge_count=1,
        executions=executions
    )
    
    assert metrics.processing_time_ms == 10.0
    assert metrics.candidate_count == 2
    assert len(metrics.executions) == 1
    assert metrics.executions[0].processor_name == "MetadataExtractor"
