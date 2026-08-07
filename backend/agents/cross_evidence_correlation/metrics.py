# -*- coding: utf-8 -*-
"""Correlation metrics builder module."""

from typing import List
from backend.agents.cross_evidence_correlation.schema import CorrelationMetrics, ProcessorExecution

class MetricsCalculator:
    """Calculates granular cross-modal correlation sub-durations."""
    
    @staticmethod
    def calculate(
        processing_time_ms: float,
        extraction_time_ms: float,
        comparison_time_ms: float,
        clustering_time_ms: float,
        validation_time_ms: float,
        executions: List[ProcessorExecution]
    ) -> CorrelationMetrics:
        """Constructs timing metrics block."""
        return CorrelationMetrics(
            processing_time_ms=round(processing_time_ms, 2),
            extraction_time_ms=round(extraction_time_ms, 2),
            comparison_time_ms=round(comparison_time_ms, 2),
            clustering_time_ms=round(clustering_time_ms, 2),
            validation_time_ms=round(validation_time_ms, 2),
            executions=executions
        )
export_metrics = MetricsCalculator
