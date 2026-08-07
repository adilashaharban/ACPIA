# -*- coding: utf-8 -*-
"""Entity resolution metrics module."""

from typing import List
from backend.agents.entity_resolution.schema import EntityMetrics, ProcessorExecution

class EntityMetricsCalculator:
    """Aggregates execution counts and builds metrics logs."""
    
    @staticmethod
    def calculate(
        processing_time_ms: float,
        candidate_count: int,
        normalization_count: int,
        match_count: int,
        merge_count: int,
        executions: List[ProcessorExecution]
    ) -> EntityMetrics:
        """Constructs performance metrics logs."""
        return EntityMetrics(
            processing_time_ms=round(processing_time_ms, 2),
            candidate_count=candidate_count,
            normalization_count=normalization_count,
            match_count=match_count,
            merge_count=merge_count,
            executions=executions
        )
