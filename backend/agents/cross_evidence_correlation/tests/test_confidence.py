# -*- coding: utf-8 -*-
"""Unit tests for ConfidenceCalculator."""

from backend.agents.cross_evidence_correlation.confidence import ConfidenceCalculator

def test_confidence_calculator() -> None:
    """Verifies that final_confidence aggregates weighted parameters correctly."""
    breakdown = ConfidenceCalculator.calculate(
        entity_score=0.90,
        temporal_score=0.80,
        location_score=0.80,
        graph_score=0.70,
        content_score=0.70
    )
    
    # 0.9*0.3 + 0.8*0.2 + 0.8*0.2 + 0.7*0.15 + 0.7*0.15 = 0.27 + 0.16 + 0.16 + 0.105 + 0.105 = 0.80
    assert breakdown.final_confidence == 0.80
