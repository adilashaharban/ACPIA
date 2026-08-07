# -*- coding: utf-8 -*-
"""Vision metrics module."""

from typing import List
from backend.agents.vision_intelligence.schema import VisionMetrics, DetectorExecution

class VisionMetricsCalculator:
    """Aggregates execution durations and builds metrics models."""
    
    @staticmethod
    def calculate(
        processing_time_ms: float,
        executions: List[DetectorExecution]
    ) -> VisionMetrics:
        """Constructs performance metrics logs.
        
        Args:
            processing_time_ms: Total pipeline runtime.
            executions: Individual detector execution logs.
            
        Returns:
            VisionMetrics object.
        """
        return VisionMetrics(
            processing_time_ms=round(processing_time_ms, 2),
            executions=executions
        )
