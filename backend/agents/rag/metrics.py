# -*- coding: utf-8 -*-
"""Retrieval metrics builder module."""

from typing import List
from backend.agents.rag.schema import RetrievalMetrics, ProcessorExecution

class MetricsCalculator:
    """Calculates granular embedding and retrieval sub-durations."""
    
    @staticmethod
    def calculate(
        processing_time_ms: float,
        indexing_time_ms: float,
        embedding_time_ms: float,
        retrieval_time_ms: float,
        executions: List[ProcessorExecution]
    ) -> RetrievalMetrics:
        """Constructs timing metrics block."""
        return RetrievalMetrics(
            processing_time_ms=round(processing_time_ms, 2),
            indexing_time_ms=round(indexing_time_ms, 2),
            embedding_time_ms=round(embedding_time_ms, 2),
            retrieval_time_ms=round(retrieval_time_ms, 2),
            executions=executions
        )
export_metrics = MetricsCalculator
