# -*- coding: utf-8 -*-
"""Entity confidence calculator."""

from typing import List
from backend.agents.entity_resolution.schema import CandidateEntity, MatchingEvidence, ConfidenceBreakdown, MatchingAlgorithm
from backend.agents.entity_resolution.constants import BASE_CONFIDENCE_WEIGHT, MULTIPLE_EVIDENCE_BOOST, MAX_BOOST_VALUE

class EntityConfidenceCalculator:
    """Calculates granular match scores and aggregates overall entity resolution confidence."""
    
    @staticmethod
    def calculate(cluster: List[CandidateEntity], matches: List[MatchingEvidence]) -> ConfidenceBreakdown:
        """Computes confidence score parameters.
        
        Args:
            cluster: Cluster candidate list.
            matches: Similarity matches references.
            
        Returns:
            ConfidenceBreakdown object.
        """
        exact_score = 0.0
        fuzzy_scores = []
        cross_modal_score = 0.0
        
        # Check matching algorithms
        for m in matches:
            if m.algorithm == MatchingAlgorithm.EXACT:
                exact_score = 1.0
            elif m.algorithm in [MatchingAlgorithm.JARO_WINKLER, MatchingAlgorithm.LEVENSHTEIN]:
                fuzzy_scores.append(m.similarity_score)
            elif m.algorithm == MatchingAlgorithm.CROSS_MODAL:
                cross_modal_score = 1.0
                
        # Average fuzzy similarity
        fuzzy_score = sum(fuzzy_scores) / len(fuzzy_scores) if fuzzy_scores else 0.0
        
        # Boost confidence based on number of supporting evidence sources
        evidence_sources = len(set([c.source_reference.evidence_id for c in cluster]))
        evidence_count_score = min(1.0, 0.5 + (evidence_sources - 1) * MULTIPLE_EVIDENCE_BOOST)
        
        # Calculate final aggregated confidence (noisy-OR approximation)
        primary_conf = max([c.confidence for c in cluster]) if cluster else 0.0
        final_conf = min(MAX_BOOST_VALUE, primary_conf + (evidence_sources - 1) * MULTIPLE_EVIDENCE_BOOST)
        
        return ConfidenceBreakdown(
            exact_match_score=exact_score,
            fuzzy_match_score=round(fuzzy_score, 4),
            cross_modal_score=cross_modal_score,
            evidence_count_score=round(evidence_count_score, 4),
            final_confidence=round(final_conf, 4)
        )
