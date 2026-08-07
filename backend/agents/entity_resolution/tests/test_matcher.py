# -*- coding: utf-8 -*-
"""Unit tests for EntityMatcher."""

from backend.agents.entity_resolution.matcher import EntityMatcher
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType, MatchingAlgorithm
from backend.schemas.common import SourceReference, DocumentElementType

def test_matcher_blocking_and_match() -> None:
    """Verifies that matcher groups by type and matches similar name pairs."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="Test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    c1 = CandidateEntity(
        candidate_id="1",
        entity_type=EntityType.PERSON,
        raw_value="John Doe",
        normalized_value="John Doe",
        confidence=0.90,
        extraction_agent="doc",
        source_reference=ref
    )
    c2 = CandidateEntity(
        candidate_id="2",
        entity_type=EntityType.PERSON,
        raw_value="Jonh Doe",
        normalized_value="Jonh Doe",
        confidence=0.90,
        extraction_agent="doc",
        source_reference=ref
    )
    
    # Check blocking
    buckets = EntityMatcher.block_candidates([c1, c2])
    assert len(buckets["PERSON"]) == 2
    
    # Check fuzzy Jaro-Winkler match
    is_match, evidence = EntityMatcher.match_pair(c1, c2)
    assert is_match is True
    assert evidence.algorithm == MatchingAlgorithm.JARO_WINKLER
    assert evidence.similarity_score > 0.90
