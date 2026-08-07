# -*- coding: utf-8 -*-
"""Audio metrics module."""

from typing import List
from backend.agents.audio_intelligence.schema import AudioMetrics, ProcessorExecution

class AudioMetricsCalculator:
    """Aggregates execution durations and builds metrics models."""
    
    @staticmethod
    def calculate(
        processing_time_ms: float,
        executions: List[ProcessorExecution]
    ) -> AudioMetrics:
        """Constructs performance metrics logs.
        
        Args:
            processing_time_ms: Total pipeline runtime.
            executions: Individual processor execution logs.
            
        Returns:
            AudioMetrics object.
        """
        return AudioMetrics(
            processing_time_ms=round(processing_time_ms, 2),
            executions=executions
        )
