# -*- coding: utf-8 -*-
"""Unit tests for validator module."""

import pytest
from backend.agents.evidence_intake.validator import EvidenceValidator
from backend.agents.evidence_intake.exceptions import (
    InvalidFileError,
    OversizedFileError,
    UnsupportedMimeTypeError,
)

def test_sanitize_filename_success() -> None:
    """Verifies that filename is cleaned and extensions kept lowercase."""
    assert EvidenceValidator.sanitize_filename("suspect_image_123.PNG") == "suspect_image_123.png"
    assert EvidenceValidator.sanitize_filename("document-report.PDF") == "document-report.pdf"
    assert EvidenceValidator.sanitize_filename("illegal*char?.txt") == "illegal_char_.txt"

def test_sanitize_filename_traversal() -> None:
    """Verifies path traversal attempt fails validation."""
    with pytest.raises(InvalidFileError):
        EvidenceValidator.sanitize_filename("../../../etc/passwd")
    with pytest.raises(InvalidFileError):
        EvidenceValidator.sanitize_filename("folder/file.txt")

def test_validate_empty_file() -> None:
    """Verifies empty bytes are rejected."""
    with pytest.raises(InvalidFileError):
        EvidenceValidator.validate(b"", "file.txt")

def test_validate_unsupported_mime() -> None:
    """Verifies invalid or dangerous extension MIME types are rejected."""
    # Executable files are not allowed
    with pytest.raises(UnsupportedMimeTypeError):
        EvidenceValidator.validate(b"MZ...", "malware.exe")

def test_validate_success() -> None:
    """Verifies a correct, clean upload passes validator successfully."""
    # Simple plain text file
    content = b"Case logs details"
    name, mime = EvidenceValidator.validate(content, "log_entry.txt")
    assert name == "log_entry.txt"
    assert mime == "text/plain"
