# -*- coding: utf-8 -*-
"""Unit tests for hashing module."""

import pytest
from backend.agents.evidence_intake.hashing import EvidenceHasher
from backend.agents.evidence_intake.exceptions import HashingError

def test_compute_hash_success() -> None:
    """Verifies that SHA-256 matches correct hex digest."""
    data = b"ACPIA Investigation Evidence Content"
    expected = "cc725bce9b6b5fd210e9a947efe6cc92a70f2aebde2ba6243dabae5b11ee8772"
    assert EvidenceHasher.compute_hash(data) == expected

def test_compute_hash_empty_string() -> None:
    """Verifies hashing works for empty bytes."""
    data = b""
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert EvidenceHasher.compute_hash(data) == expected

def test_compute_hash_failure_none() -> None:
    """Verifies exception is raised when passing None."""
    with pytest.raises(HashingError):
        EvidenceHasher.compute_hash(None)  # type: ignore
