# -*- coding: utf-8 -*-
"""Unit tests for EntityMerger."""

from backend.agents.entity_resolution.merger import EntityMerger
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType, ConfidenceBreakdown, MatchingEvidence, MatchingAlgorithm
from backend.schemas.common import SourceReference, DocumentElementType

def test_entity_merger() -> None:
    """Verifies that merger combines source reference lists and builds alias logs."""
    ref1 = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="Test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    ref2 = SourceReference(
        evidence_id="EVID-2",
        file_path="other.txt",
        page_number=2,
        parser="Test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    c1 = CandidateEntity(
        candidate_id="c1",
        entity_type=EntityType.PERSON,
        raw_value="John Doe",
        normalized_value="John Doe",
        confidence=0.90,
        extraction_agent="doc",
        source_reference=ref1
    )
    c2 = CandidateEntity(
        candidate_id="c2",
        entity_type=EntityType.PERSON,
        raw_value="Jonh Doe",
        normalized_value="Jonh Doe",
        confidence=0.85,
        extraction_agent="doc",
        source_reference=ref2
    )
    
    breakdown = ConfidenceBreakdown(
        exact_match_score=0.0,
        fuzzy_match_score=0.95,
        cross_modal_score=0.0,
        evidence_count_score=0.55,
        final_confidence=0.92
    )
    
    evidence = MatchingEvidence(
        observation_id="c2",
        algorithm=MatchingAlgorithm.JARO_WINKLER,
        similarity_score=0.95,
        matched_fields=["normalized_value"]
    )
    
    canonical = EntityMerger.merge_cluster([c1, c2], [evidence], breakdown)
    assert canonical.canonical_name == "John Doe"
    assert len(canonical.aliases) == 1
    assert canonical.aliases[0].alias_name == "Jonh Doe"
    assert len(canonical.linked_evidence) == 2
    assert "EVID-1" in canonical.linked_evidence
    assert "EVID-2" in canonical.linked_evidence
