# -*- coding: utf-8 -*-
"""Timeline metrics builder module."""

from typing import List
from backend.agents.timeline_intelligence.schema import TimelineMetrics, ProcessorExecution

class TimelineMetricsCalculator:
    """Calculates granular timeline execution durations."""
    
    @staticmethod
    def calculate(
        processing_time_ms: float,
        timestamp_normalization_time_ms: float,
        merge_time_ms: float,
        sorting_time_ms: float,
        validation_time_ms: float,
        builder_time_ms: float,
        executions: List[ProcessorExecution]
    ) -> TimelineMetrics:
        """Constructs timing metrics block."""
        return TimelineMetrics(
            processing_time_ms=round(processing_time_ms, 2),
            timestamp_normalization_time_ms=round(timestamp_normalization_time_ms, 2),
            merge_time_ms=round(merge_time_ms, 2),
            sorting_time_ms=round(sorting_time_ms, 2),
            validation_time_ms=round(validation_time_ms, 2),
            builder_time_ms=round(builder_time_ms, 2),
            executions=executions
        )
