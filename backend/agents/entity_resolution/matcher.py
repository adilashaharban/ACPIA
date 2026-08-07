# -*- coding: utf-8 -*-
"""Entity matching and blocking module using rapidfuzz."""

from typing import List, Dict, Tuple, Optional
from rapidfuzz.distance import JaroWinkler, Levenshtein
from backend.agents.entity_resolution.schema import CandidateEntity, MatchingEvidence, MatchingAlgorithm
from backend.agents.entity_resolution.constants import FUZZY_JARO_WINKLER_THRESHOLD, FUZZY_LEVENSHTEIN_MAX_DISTANCE

class EntityMatcher:
    """Matches candidate entities against resolved CanonicalEntity references."""
    
    @staticmethod
    def block_candidates(candidates: List[CandidateEntity]) -> Dict[str, List[CandidateEntity]]:
        """Buckets candidates by entity type to limit pairwise comparisons.
        
        Args:
            candidates: List of CandidateEntity.
            
        Returns:
            Dictionary mapping entity type name to a list of CandidateEntity items.
        """
        buckets: Dict[str, List[CandidateEntity]] = {}
        for candidate in candidates:
            t = candidate.entity_type.name
            if t not in buckets:
                buckets[t] = []
            buckets[t].append(candidate)
        return buckets

    @staticmethod
    def match_pair(c1: CandidateEntity, c2: CandidateEntity) -> Tuple[bool, Optional[MatchingEvidence]]:
        """Compares a pair of candidate entities.
        
        Args:
            c1: First candidate.
            c2: Second candidate.
            
        Returns:
            Tuple containing (is_match, MatchingEvidence object or None).
        """
        # 1. Exact match checks on normalized values
        if c1.normalized_value == c2.normalized_value:
            evidence = MatchingEvidence(
                observation_id=c2.candidate_id,
                algorithm=MatchingAlgorithm.EXACT,
                similarity_score=1.0,
                matched_fields=["normalized_value"]
            )
            return True, evidence
            
        # 2. Fuzzy matches for strings (Person names or locations)
        val1, val2 = c1.normalized_value, c2.normalized_value
        
        # Calculate Jaro-Winkler similarity
        sim = JaroWinkler.similarity(val1, val2)
        if sim >= FUZZY_JARO_WINKLER_THRESHOLD:
            evidence = MatchingEvidence(
                observation_id=c2.candidate_id,
                algorithm=MatchingAlgorithm.JARO_WINKLER,
                similarity_score=round(float(sim), 4),
                matched_fields=["normalized_value"]
            )
            return True, evidence
            
        # Levenshtein distance check (e.g. slight typos/variations)
        dist = Levenshtein.distance(val1, val2)
        if dist <= FUZZY_LEVENSHTEIN_MAX_DISTANCE:
            evidence = MatchingEvidence(
                observation_id=c2.candidate_id,
                algorithm=MatchingAlgorithm.LEVENSHTEIN,
                similarity_score=round(1.0 - (dist / max(len(val1), len(val2), 1)), 4),
                matched_fields=["normalized_value"]
            )
            return True, evidence
            
        return False, None
