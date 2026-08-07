# -*- coding: utf-8 -*-
"""Unit tests for Validator."""

import pytest
from pathlib import Path
from backend.agents.rag.validator import Validator
from backend.agents.rag.exceptions import ChecksumMismatchError

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
