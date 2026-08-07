# -*- coding: utf-8 -*-
"""Unit tests for EntityValidator."""

import pytest
from pathlib import Path
from backend.agents.entity_resolution.validator import EntityValidator
from backend.agents.entity_resolution.exceptions import ChecksumMismatchError
from backend.agents.entity_resolution.schema import CanonicalEntity, EntityType, ConfidenceBreakdown
from backend.schemas.common import SourceReference, DocumentElementType

def test_verify_integrity_success(mock_evidence_file: Path) -> None:
    """Verifies that matching SHA hashes complete validation successfully."""
    import hashlib
    content = mock_evidence_file.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    # Should not raise exception
    EntityValidator.verify_integrity(str(mock_evidence_file.resolve()), sha256)

def test_verify_integrity_mismatch(mock_evidence_file: Path) -> None:
    """Verifies that mismatching hashes raise ChecksumMismatchError."""
    bad_hash = "wrongsha"
    with pytest.raises(ChecksumMismatchError):
        EntityValidator.verify_integrity(str(mock_evidence_file.resolve()), bad_hash)

def test_validate_entities_invalid_phone() -> None:
    """Verifies coordinate checks flag warnings on invalid phone formats."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="Test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    breakdown = ConfidenceBreakdown(
        exact_match_score=1.0,
        fuzzy_match_score=0.0,
        cross_modal_score=0.0,
        evidence_count_score=0.5,
        final_confidence=0.90
    )
    
    # Phone number with invalid non-E.164 pattern
    ent = CanonicalEntity(
        entity_id="ENT-PHO-1",
        entity_type=EntityType.PHONE,
        canonical_name="999-invalid-phone",
        confidence_breakdown=breakdown,
        source_references=[ref],
        supporting_observations=[],
        linked_evidence=["EVID-1"],
        creation_method="EXACT_MATCH"
    )
    
    validation = EntityValidator.validate_entities([ent])
    assert len(validation.warnings) == 1
    assert "E.164" in validation.warnings[0]
