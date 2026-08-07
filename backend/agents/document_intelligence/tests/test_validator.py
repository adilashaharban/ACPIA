# -*- coding: utf-8 -*-
"""Unit tests for DocumentValidator."""

import pytest
from pathlib import Path
from backend.agents.document_intelligence.validator import DocumentValidator
from backend.agents.document_intelligence.exceptions import ChecksumMismatchError
from backend.agents.document_intelligence.schema import Table, Page

def test_verify_integrity_success(mock_txt: Path) -> None:
    """Verifies matching hash validation completes successfully."""
    import hashlib
    content = mock_txt.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    
    # Should not raise exception
    DocumentValidator.verify_integrity(str(mock_txt.resolve()), sha256)

def test_verify_integrity_mismatch(mock_txt: Path) -> None:
    """Verifies that mismatching hash triggers ChecksumMismatchError."""
    bad_hash = "c0ffee1234567890abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdef"
    with pytest.raises(ChecksumMismatchError):
        DocumentValidator.verify_integrity(str(mock_txt.resolve()), bad_hash)

def test_validate_structure_warnings() -> None:
    """Verifies warning triggers for cell count inconsistencies."""
    # 2x2 table but contains only 3 cells (1 cell missing)
    table = Table(
        table_id="T1",
        page_number=1,
        rows_count=2,
        cols_count=2,
        cells=[],
        headers=[],
        reading_order=0
    )
    
    validation = DocumentValidator.validate_structure(
        pages=[Page(page_number=1, text_content="", paragraphs=[], tables=[table], forms=[])],
        tables=[table]
    )
    
    assert len(validation.warnings) == 1
    assert "cells count mismatch" in validation.warnings[0]
