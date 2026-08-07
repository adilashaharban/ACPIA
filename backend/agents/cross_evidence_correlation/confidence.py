# -*- coding: utf-8 -*-
"""Confidence aggregation module."""

from backend.agents.cross_evidence_correlation.schema import CorrelationConfidenceBreakdown
from backend.agents.cross_evidence_correlation.constants import (
    WEIGHT_ENTITY, WEIGHT_TEMPORAL, WEIGHT_LOCATION, WEIGHT_GRAPH, WEIGHT_CONTENT
)

class ConfidenceCalculator:
    """Calculates weighted multivariable confidence breakdowns."""
    
    @staticmethod
    def calculate(
        entity_score: float = 0.0,
        temporal_score: float = 0.0,
        location_score: float = 0.0,
        graph_score: float = 0.0,
        content_score: float = 0.0
    ) -> CorrelationConfidenceBreakdown:
        """Assembles scoring parameters.
        
        Returns:
            CorrelationConfidenceBreakdown object.
        """
        final_conf = (
            (entity_score * WEIGHT_ENTITY) +
            (temporal_score * WEIGHT_TEMPORAL) +
            (location_score * WEIGHT_LOCATION) +
            (graph_score * WEIGHT_GRAPH) +
            (content_score * WEIGHT_CONTENT)
        )
        
        return CorrelationConfidenceBreakdown(
            entity_score=round(entity_score, 4),
            temporal_score=round(temporal_score, 4),
            location_score=round(location_score, 4),
            graph_score=round(graph_score, 4),
            content_score=round(content_score, 4),
            final_confidence=round(final_conf, 4)
        )
export_confidence = ConfidenceCalculator
