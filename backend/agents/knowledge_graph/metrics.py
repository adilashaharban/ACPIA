# -*- coding: utf-8 -*-
"""Graph metrics builder."""

from typing import List
from backend.agents.knowledge_graph.schema import GraphMetrics, ProcessorExecution

class GraphMetricsCalculator:
    """Calculates granular graph compilation metrics."""
    
    @staticmethod
    def calculate(
        processing_time_ms: float,
        node_build_time_ms: float,
        edge_build_time_ms: float,
        validation_time_ms: float,
        repository_time_ms: float,
        executions: List[ProcessorExecution]
    ) -> GraphMetrics:
        """Constructs timing metrics block."""
        return GraphMetrics(
            processing_time_ms=round(processing_time_ms, 2),
            node_build_time_ms=round(node_build_time_ms, 2),
            edge_build_time_ms=round(edge_build_time_ms, 2),
            validation_time_ms=round(validation_time_ms, 2),
            repository_time_ms=round(repository_time_ms, 2),
            executions=executions
        )
