# -*- coding: utf-8 -*-
"""Unit tests for Validator."""

import pytest
from pathlib import Path
from backend.agents.investigation_reasoning.validator import Validator
from backend.agents.investigation_reasoning.exceptions import ChecksumMismatchError
from backend.agents.investigation_reasoning.schema import Finding, FindingStatus, FindingType, ReasoningConfidence

def test_verify_integrity_success(mock_evidence_file: Path) -> None:
    """Verifies SHA checksums validation."""
    import hashlib
    content = mock_evidence_file.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    Validator.verify_integrity(str(mock_evidence_file.resolve()), sha256)

def test_verify_integrity_mismatch(mock_evidence_file: Path) -> None:
    """Verifies that mismatching checksums raise ChecksumMismatchError."""
    with pytest.raises(ChecksumMismatchError):
        Validator.verify_integrity(str(mock_evidence_file.resolve()), "badsha")

def test_validate_package() -> None:
    """Verifies unique finding ID validations."""
    conf = ReasoningConfidence(
        evidence_score=0.90, retrieval_score=0.90, citation_score=0.90,
        consistency_score=1.0, model_score=0.90, final_score=0.92
    )
    
    f1 = Finding(
        finding_id="F1",
        title="F1",
        description="F1 description",
        finding_type=FindingType.FACTUAL_OBSERVATION,
        finding_status=FindingStatus.SUPPORTED,
        confidence=conf
    )
    
    f2 = Finding(
        finding_id="F1",
        title="F2",
        description="F2 description",
        finding_type=FindingType.FACTUAL_OBSERVATION,
        finding_status=FindingStatus.SUPPORTED,
        confidence=conf
    )
    
    validation = Validator.validate_package([f1, f2], [])
    assert validation.integrity_status == "FAIL"
    assert len(validation.errors) == 1
export_test_validator = test_validate_package
