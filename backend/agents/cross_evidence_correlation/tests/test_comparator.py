# -*- coding: utf-8 -*-
"""Unit tests for Comparator."""

from datetime import datetime, timezone
from backend.agents.cross_evidence_correlation.comparator import Comparator
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType
from backend.schemas.common import SourceReference, DocumentElementType

def test_comparator() -> None:
    """Verifies that similarity computes correct metric ratings."""
    ref = SourceReference(
        evidence_id="E1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    o1 = CandidateObservation(
        candidate_id="CD-1",
        observation_type=CorrelationType.ENTITY_MATCH,
        originating_agent="test",
        evidence_id="E1",
        raw_value="John Doe",
        normalized_value="john doe",
        confidence=1.0,
        timestamp=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc),
        latitude=12.97,
        longitude=77.59,
        source_reference=ref
    )
    
    o2 = CandidateObservation(
        candidate_id="CD-2",
        observation_type=CorrelationType.ENTITY_MATCH,
        originating_agent="test",
        evidence_id="E1",
        raw_value="John A Doe",
        normalized_value="john a doe",
        confidence=1.0,
        timestamp=datetime(2026, 8, 1, 10, 0, 10, tzinfo=timezone.utc),
        latitude=12.971,
        longitude=77.591,
        source_reference=ref
    )
    
    sim = Comparator.entity_similarity(o1, o2)
    assert sim > 0.80
    
    diff = Comparator.temporal_difference_seconds(o1, o2)
    assert diff == 10.0
    
    dist = Comparator.gps_distance_meters(o1, o2)
    assert dist is not None
    assert dist < 300.0  # within 300m
