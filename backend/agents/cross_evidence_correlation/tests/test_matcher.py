# -*- coding: utf-8 -*-
"""Unit tests for Matcher."""

from datetime import datetime, timezone
from backend.agents.cross_evidence_correlation.comparator import Comparator
from backend.agents.cross_evidence_correlation.matcher import Matcher
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType, CorrelationStrength
from backend.schemas.common import SourceReference, DocumentElementType

def test_matcher() -> None:
    """Verifies that similarity thresholds yield verified matches."""
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
        source_reference=ref
    )
    
    o2 = CandidateObservation(
        candidate_id="CD-2",
        observation_type=CorrelationType.ENTITY_MATCH,
        originating_agent="test",
        evidence_id="E1",
        raw_value="John Doe",
        normalized_value="john doe",
        confidence=1.0,
        source_reference=ref
    )
    
    matcher = Matcher(Comparator())
    match = matcher.match_candidates(o1, o2)
    assert match is not None
    assert match.correlation_strength == CorrelationStrength.STRONG or match.correlation_strength == CorrelationStrength.EXACT
