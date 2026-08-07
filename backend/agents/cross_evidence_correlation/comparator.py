# -*- coding: utf-8 -*-
"""Pairwise candidate comparator."""

import math
from datetime import timezone
from typing import Optional
from backend.agents.cross_evidence_correlation.schema import CandidateObservation

try:
    from rapidfuzz import fuzz
except ImportError:
    import difflib
    class fuzz:
        @staticmethod
        def ratio(s1: str, s2: str) -> float:
            return difflib.SequenceMatcher(None, s1, s2).ratio() * 100.0


class Comparator:
    """Responsible ONLY for computing similarities between observations."""
    
    @staticmethod
    def entity_similarity(o1: CandidateObservation, o2: CandidateObservation) -> float:
        """Computes rapidfuzz name similarity ratio."""
        if not o1.normalized_value or not o2.normalized_value:
            return 0.0
        return fuzz.ratio(o1.normalized_value, o2.normalized_value) / 100.0

    @staticmethod
    def temporal_difference_seconds(o1: CandidateObservation, o2: CandidateObservation) -> Optional[float]:
        """Calculates absolute difference in seconds."""
        if not o1.timestamp or not o2.timestamp:
            return None
            
        t1 = o1.timestamp
        t2 = o2.timestamp
        if t1.tzinfo is None:
            t1 = t1.replace(tzinfo=timezone.utc)
        else:
            t1 = t1.astimezone(timezone.utc)
            
        if t2.tzinfo is None:
            t2 = t2.replace(tzinfo=timezone.utc)
        else:
            t2 = t2.astimezone(timezone.utc)
            
        return abs((t1 - t2).total_seconds())

    @staticmethod
    def gps_distance_meters(o1: CandidateObservation, o2: CandidateObservation) -> Optional[float]:
        """Haversine formula to compute distance in meters."""
        if o1.latitude is None or o1.longitude is None or o2.latitude is None or o2.longitude is None:
            return None
            
        # Earth radius in meters
        r = 6371000.0
        phi1 = math.radians(o1.latitude)
        phi2 = math.radians(o2.latitude)
        dphi = math.radians(o2.latitude - o1.latitude)
        dlambda = math.radians(o2.longitude - o1.longitude)
        
        a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c
export_comparator = Comparator
