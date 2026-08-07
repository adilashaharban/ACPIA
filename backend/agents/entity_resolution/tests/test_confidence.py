# -*- coding: utf-8 -*-
"""Unit tests for EntityConfidenceCalculator."""

from backend.agents.entity_resolution.confidence import EntityConfidenceCalculator
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType, MatchingEvidence, MatchingAlgorithm
from backend.schemas.common import SourceReference, DocumentElementType

def test_confidence_calculations() -> None:
    """Verifies confidence calculations aggregate matching properties."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="Test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    c = CandidateEntity(
        candidate_id="c1",
        entity_type=EntityType.PERSON,
        raw_value="John Doe",
        normalized_value="John Doe",
        confidence=0.90,
        extraction_agent="doc",
        source_reference=ref
    )
    
    m = MatchingEvidence(
        observation_id="c2",
        algorithm=MatchingAlgorithm.EXACT,
        similarity_score=1.0,
        matched_fields=["normalized_value"]
    )
    
    breakdown = EntityConfidenceCalculator.calculate([c], [m])
    assert breakdown.exact_match_score == 1.0
    assert breakdown.final_confidence == 0.90
