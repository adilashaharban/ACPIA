# -*- coding: utf-8 -*-
"""Unit tests for ConflictDetector."""

from datetime import datetime, timezone
from backend.agents.cross_evidence_correlation.conflict_detector import ConflictDetector
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType, ConflictType
from backend.schemas.common import SourceReference, DocumentElementType

def test_conflict_detector() -> None:
    """Verifies that distant coordinate entries for the same entity at the same time raise conflicts."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    o1 = CandidateObservation(
        candidate_id="CD-1",
        observation_type=CorrelationType.LOCATION_MATCH,
        originating_agent="test",
        evidence_id="EVID-1",
        raw_value="12.97,77.59",
        normalized_value="12.97,77.59",
        confidence=1.0,
        timestamp=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc),
        latitude=12.97,
        longitude=77.59,
        entity_id="ENT-PER-1",
        source_reference=ref
    )
    
    o2 = CandidateObservation(
        candidate_id="CD-2",
        observation_type=CorrelationType.LOCATION_MATCH,
        originating_agent="test",
        evidence_id="EVID-2",
        raw_value="13.97,78.59",
        normalized_value="13.97,78.59",
        confidence=1.0,
        timestamp=datetime(2026, 8, 1, 10, 2, 0, tzinfo=timezone.utc),
        latitude=13.97,
        longitude=78.59,
        entity_id="ENT-PER-1",
        source_reference=ref
    )
    
    conflicts = ConflictDetector.detect_conflicts([o1, o2])
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == ConflictType.LOCATION_CONFLICT
