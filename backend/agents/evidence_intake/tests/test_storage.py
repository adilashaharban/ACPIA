# -*- coding: utf-8 -*-
"""Unit tests for storage module."""

from pathlib import Path
import pytest
from backend.agents.evidence_intake.storage import LocalStorageProvider

def test_local_storage_store(tmp_path: Path) -> None:
    """Verifies that the LocalStorageProvider writes files to correct path structures."""
    provider = LocalStorageProvider(base_dir=tmp_path)
    
    file_bytes = b"Image data payload"
    case_id = "CASE-902"
    filename = "suspect_photo.png"
    sha256 = "c0ffee1234567890abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdef"
    
    file_path, obj_path = provider.store(
        file_bytes=file_bytes,
        case_id=case_id,
        filename=filename,
        sha256_hash=sha256
    )
    
    # Assert physical write occurred
    written_file = Path(file_path)
    assert written_file.exists()
    assert written_file.read_bytes() == file_bytes
    
    # Assert path folder structure contains prefixes
    assert "cases" in file_path
    assert case_id in file_path
    assert "c0" in file_path
    assert "ff" in file_path
    
    # Assert simulated object storage path
    assert obj_path.startswith("s3://acpia-evidence/")
