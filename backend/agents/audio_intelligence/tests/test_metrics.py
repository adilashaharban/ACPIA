# -*- coding: utf-8 -*-
"""Unit tests for AudioMetricsCalculator."""

from backend.agents.audio_intelligence.metrics import AudioMetricsCalculator
from backend.agents.audio_intelligence.schema import ProcessorExecution

def test_metrics_calculator() -> None:
    """Verifies that stats computes correct execution times."""
    executions = [
        ProcessorExecution(
            processor_name="TranscriptionProcessor",
            processor_version="1.0.0",
            execution_time_ms=50.0,
            status="SUCCESS"
        )
    ]
    
    metrics = AudioMetricsCalculator.calculate(60.0, executions)
    assert metrics.processing_time_ms == 60.0
    assert len(metrics.executions) == 1
    assert metrics.executions[0].processor_name == "TranscriptionProcessor"
