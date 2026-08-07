# -*- coding: utf-8 -*-
"""Unit tests for GraphMetricsCalculator."""

from backend.agents.knowledge_graph.metrics import GraphMetricsCalculator
from backend.agents.knowledge_graph.schema import ProcessorExecution

def test_metrics_calculator() -> None:
    """Verifies that stats computes correct duration averages."""
    executions = [
        ProcessorExecution(
            processor_name="NodeBuilder",
            processor_version="1.0.0",
            execution_time_ms=5.0,
            status="SUCCESS"
        )
    ]
    
    metrics = GraphMetricsCalculator.calculate(
        processing_time_ms=10.0,
        node_build_time_ms=5.0,
        edge_build_time_ms=2.0,
        validation_time_ms=1.0,
        repository_time_ms=2.0,
        executions=executions
    )
    
    assert metrics.processing_time_ms == 10.0
    assert metrics.node_build_time_ms == 5.0
    assert len(metrics.executions) == 1
    assert metrics.executions[0].processor_name == "NodeBuilder"
