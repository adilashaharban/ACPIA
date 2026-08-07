# -*- coding: utf-8 -*-
"""Unit tests for ConfidenceCalculator."""

from backend.agents.investigation_reasoning.confidence_calculator import ConfidenceCalculator

def test_confidence_calculator() -> None:
    """Verifies final reasoning confidence aggregates correctly."""
    conf = ConfidenceCalculator.calculate_confidence(
        evidence_score=0.90,
        retrieval_score=0.90,
        citation_score=0.90,
        consistency_score=1.0,
        model_score=0.90
    )
    
    # (0.9*4 + 1.0)/5 = 4.6 / 5 = 0.92
    assert conf.final_score == 0.92
