# -*- coding: utf-8 -*-
"""Correlation conflict detector."""

import uuid
from typing import List, Dict
from backend.agents.cross_evidence_correlation.schema import (
    CorrelationConflict, CandidateObservation, ConflictType, CorrelationObservation
)

class ConflictDetector:
    """Scans candidates for spatial-temporal inconsistencies."""
    
    @staticmethod
    def detect_conflicts(candidates: List[CandidateObservation]) -> List[CorrelationConflict]:
        """Flags locations contradictions.
        
        Args:
            candidates: Extracted CandidateObservation list.
            
        Returns:
            List of CorrelationConflict warnings.
        """
        conflicts: List[CorrelationConflict] = []
        
        # Simple Location Conflict scan:
        # Group candidates by entity_id
        entity_obs: Dict[str, List[CandidateObservation]] = {}
        for c in candidates:
            if c.entity_id:
                entity_obs.setdefault(c.entity_id, []).append(c)
                
        for ent_id, obs_list in entity_obs.items():
            # Check pairwise location overlaps
            for i in range(len(obs_list)):
                o1 = obs_list[i]
                for j in range(i + 1, len(obs_list)):
                    o2 = obs_list[j]
                    
                    if o1.timestamp and o2.timestamp and o1.latitude is not None and o2.latitude is not None:
                        time_diff = abs((o1.timestamp - o2.timestamp).total_seconds())
                        
                        # If occurred within 10 minutes (600s) but coordinates are different
                        dist_diff = abs(o1.latitude - o2.latitude) + abs(o1.longitude - o2.longitude)
                        if time_diff <= 600.0 and dist_diff > 0.05:
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
                            
                            conflicts.append(
                                CorrelationConflict(
                                    conflict_id=f"CFL-{str(uuid.uuid4())[:8]}",
                                    conflict_type=ConflictType.LOCATION_CONFLICT,
                                    description=f"Entity {ent_id} observed at distant locations within {time_diff}s.",
                                    conflicting_observations=[obs1, obs2],
                                    confidence=1.0
                                )
                            )
                            
        return conflicts
export_conflict_detector = ConflictDetector
