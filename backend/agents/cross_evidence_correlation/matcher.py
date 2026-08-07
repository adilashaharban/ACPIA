# -*- coding: utf-8 -*-
"""Correlation matcher module."""

import uuid
from typing import List, Optional
from backend.agents.cross_evidence_correlation.schema import (
    CorrelationMatch, CandidateObservation, CorrelationType, CorrelationStrength,
    CorrelationObservation, CorrelationEvidence
)
from backend.agents.cross_evidence_correlation.constants import (
    ENTITY_SIMILARITY_THRESHOLD, TEMPORAL_TOLERANCE_SECONDS, GPS_RADIUS_METERS
)
from backend.agents.cross_evidence_correlation.comparator import Comparator

class Matcher:
    """Evaluates candidate similarity scores and returns matching links."""
    
    def __init__(self, comparator: Comparator) -> None:
        self.comparator = comparator

    def match_candidates(self, o1: CandidateObservation, o2: CandidateObservation) -> Optional[CorrelationMatch]:
        """Compares two normalized candidates.
        
        Args:
            o1: Candidate 1.
            o2: Candidate 2.
            
        Returns:
            CorrelationMatch if a link is found, else None.
        """
        # Skip matching the exact same candidate
        if o1.candidate_id == o2.candidate_id:
            return None
            
        # Match resolved Entity ID first
        if o1.entity_id and o2.entity_id and o1.entity_id == o2.entity_id:
            return self._build_match(
                o1=o1,
                o2=o2,
                c_type=CorrelationType.ENTITY_MATCH,
                strength=CorrelationStrength.EXACT,
                algo="EXACT_ENTITY_ID_MATCH",
                fields=["entity_id"],
                confidence=min(o1.confidence, o2.confidence)
            )
            
        # Match Entity name similarity
        if o1.observation_type == CorrelationType.ENTITY_MATCH and o2.observation_type == CorrelationType.ENTITY_MATCH:
            sim = self.comparator.entity_similarity(o1, o2)
            if sim >= ENTITY_SIMILARITY_THRESHOLD:
                strength = CorrelationStrength.STRONG if sim >= 0.95 else CorrelationStrength.MODERATE
                return self._build_match(
                    o1=o1,
                    o2=o2,
                    c_type=CorrelationType.ENTITY_MATCH,
                    strength=strength,
                    algo="LEVENSHTEIN_SIMILARITY",
                    fields=["canonical_name"],
                    confidence=sim * min(o1.confidence, o2.confidence)
                )
                
        # Match GPS proximity
        if o1.observation_type == CorrelationType.LOCATION_MATCH and o2.observation_type == CorrelationType.LOCATION_MATCH:
            dist = self.comparator.gps_distance_meters(o1, o2)
            if dist is not None and dist <= GPS_RADIUS_METERS:
                strength = CorrelationStrength.EXACT if dist == 0.0 else CorrelationStrength.STRONG
                return self._build_match(
                    o1=o1,
                    o2=o2,
                    c_type=CorrelationType.LOCATION_MATCH,
                    strength=strength,
                    algo="HAVERSINE_GPS_RADIUS",
                    fields=["latitude", "longitude"],
                    confidence=min(o1.confidence, o2.confidence)
                )
                
        # Match Temporal proximity
        if o1.observation_type == CorrelationType.TEMPORAL_MATCH and o2.observation_type == CorrelationType.TEMPORAL_MATCH:
            diff = self.comparator.temporal_difference_seconds(o1, o2)
            if diff is not None and diff <= TEMPORAL_TOLERANCE_SECONDS:
                strength = CorrelationStrength.STRONG if diff <= 5.0 else CorrelationStrength.MODERATE
                return self._build_match(
                    o1=o1,
                    o2=o2,
                    c_type=CorrelationType.TEMPORAL_MATCH,
                    strength=strength,
                    algo="TEMPORAL_TOLERANCE_WINDOW",
                    fields=["timestamp"],
                    confidence=min(o1.confidence, o2.confidence)
                )
                
        return None

    def _build_match(
        self,
        o1: CandidateObservation,
        o2: CandidateObservation,
        c_type: CorrelationType,
        strength: CorrelationStrength,
        algo: str,
        fields: List[str],
        confidence: float
    ) -> CorrelationMatch:
        obs1 = CorrelationObservation(
            observation_id=o1.candidate_id,
            evidence_id=o1.evidence_id,
            originating_agent=o1.originating_agent,
            raw_value=o1.raw_value,
            normalized_value=o1.normalized_value,
            confidence=o1.confidence,
            source_reference=o1.source_reference
        )
        obs2 = CorrelationObservation(
            observation_id=o2.candidate_id,
            evidence_id=o2.evidence_id,
            originating_agent=o2.originating_agent,
            raw_value=o2.raw_value,
            normalized_value=o2.normalized_value,
            confidence=o2.confidence,
            source_reference=o2.source_reference
        )
        
        # Build mock evidence references
        ev1 = CorrelationEvidence(
            evidence_id=o1.evidence_id,
            evidence_type="FILE",
            file_name=o1.source_reference.file_path,
            source_reference=o1.source_reference
        )
        ev2 = CorrelationEvidence(
            evidence_id=o2.evidence_id,
            evidence_type="FILE",
            file_name=o2.source_reference.file_path,
            source_reference=o2.source_reference
        )
        
        return CorrelationMatch(
            match_id=f"MTH-{c_type.name[:3]}-{str(uuid.uuid4())[:8]}",
            correlation_type=c_type,
            correlation_strength=strength,
            confidence=round(confidence, 4),
            matching_algorithm=algo,
            matched_fields=fields,
            supporting_observations=[obs1, obs2],
            supporting_evidence=[ev1, ev2]
        )
export_matcher = Matcher
