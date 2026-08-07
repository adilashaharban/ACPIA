# -*- coding: utf-8 -*-
"""Confidence calculator module."""

from backend.agents.investigation_reasoning.schema import ReasoningConfidence

class ConfidenceCalculator:
    """Calculates multidimensional confidence details for findings."""
    
    @staticmethod
    def calculate_confidence(
        evidence_score: float = 0.90,
        retrieval_score: float = 0.85,
        citation_score: float = 0.90,
        consistency_score: float = 1.0,
        model_score: float = 0.90
    ) -> ReasoningConfidence:
        """Assembles scoring parameters.
        
        Returns:
            ReasoningConfidence object.
        """
        final = (
            evidence_score +
            retrieval_score +
            citation_score +
            consistency_score +
            model_score
        ) / 5.0
        
        return ReasoningConfidence(
            evidence_score=round(evidence_score, 4),
            retrieval_score=round(retrieval_score, 4),
            citation_score=round(citation_score, 4),
            consistency_score=round(consistency_score, 4),
            model_score=round(model_score, 4),
            final_score=round(final, 4)
        )
export_confidence_calculator = ConfidenceCalculator
