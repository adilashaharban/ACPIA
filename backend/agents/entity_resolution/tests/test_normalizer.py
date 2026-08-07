# -*- coding: utf-8 -*-
"""Unit tests for EntityNormalizer."""

from backend.agents.entity_resolution.normalizer import EntityNormalizer
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType
from backend.schemas.common import SourceReference, DocumentElementType

def test_normalization() -> None:
    """Verifies that phone numbers parse to E.164 and emails to lowercase."""
    assert EntityNormalizer.normalize_email("  TEST@Domain.Com  ") == "test@domain.com"
    # Valid phone parsing (IN country format fallback)
    assert EntityNormalizer.normalize_phone("9999988888") == "+919999988888"
    assert EntityNormalizer.normalize_generic("  hello   world  ") == "hello world"
    
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
        entity_type=EntityType.EMAIL,
        raw_value="  Test@Domain.com ",
        normalized_value="",
        confidence=0.90,
        extraction_agent="doc",
        source_reference=ref
    )
    
    normalized = EntityNormalizer.normalize_candidate(c)
    assert normalized.normalized_value == "test@domain.com"
