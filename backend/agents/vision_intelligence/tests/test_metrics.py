# -*- coding: utf-8 -*-
"""Unit tests for VisionMetricsCalculator."""

from backend.agents.vision_intelligence.metrics import VisionMetricsCalculator
from backend.agents.vision_intelligence.schema import DetectorExecution

def test_metrics_calculator() -> None:
    """Verifies that stats computes correct execution times."""
    executions = [
        DetectorExecution(
            detector_name="FaceDetector",
            detector_version="1.0.0",
            execution_time_ms=12.5,
            status="SUCCESS"
        )
    ]
    
    metrics = VisionMetricsCalculator.calculate(15.0, executions)
    assert metrics.processing_time_ms == 15.0
    assert len(metrics.executions) == 1
    assert metrics.executions[0].detector_name == "FaceDetector"
