# -*- coding: utf-8 -*-
"""Reasoning metrics builder module."""

from typing import List, Optional
from backend.agents.investigation_reasoning.schema import ReasoningMetrics, ProcessorExecution, ProviderResponseMetadata

class MetricsCalculator:
    """Calculates granular reasoning sub-durations."""
    
    @staticmethod
    def calculate(
        processing_time_ms: float,
        prompt_time_ms: float,
        parsing_time_ms: float,
        validation_time_ms: float,
        provider_metadata: Optional[ProviderResponseMetadata],
        executions: List[ProcessorExecution]
    ) -> ReasoningMetrics:
        """Constructs timing metrics block."""
        return ReasoningMetrics(
            processing_time_ms=round(processing_time_ms, 2),
            prompt_time_ms=round(prompt_time_ms, 2),
            parsing_time_ms=round(parsing_time_ms, 2),
            validation_time_ms=round(validation_time_ms, 2),
            provider_metadata=provider_metadata,
            executions=executions
        )
export_metrics = MetricsCalculator
