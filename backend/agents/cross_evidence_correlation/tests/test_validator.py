# -*- coding: utf-8 -*-
"""Unit tests for Validator."""

import pytest
from pathlib import Path
from backend.agents.cross_evidence_correlation.validator import Validator
from backend.agents.cross_evidence_correlation.exceptions import ChecksumMismatchError
from backend.agents.cross_evidence_correlation.schema import CorrelationCluster

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
    """Verifies cluster ID validations."""
    c1 = CorrelationCluster(
        cluster_id="CL-1",
        cluster_name="Cluster 1",
        confidence=1.0
    )
    c2 = CorrelationCluster(
        cluster_id="CL-1",
        cluster_name="Cluster 2",
        confidence=1.0
    )
    
    validation = Validator.validate_package([c1, c2], [])
    assert validation.integrity_status == "FAIL"
    assert len(validation.errors) == 1
    assert "Duplicate cluster IDs" in validation.errors[0]
