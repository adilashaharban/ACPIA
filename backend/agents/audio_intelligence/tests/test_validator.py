# -*- coding: utf-8 -*-
"""Unit tests for AudioValidator."""

import pytest
from pathlib import Path
from backend.agents.audio_intelligence.validator import AudioValidator
from backend.agents.audio_intelligence.exceptions import ChecksumMismatchError
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.audio_intelligence.schema import SpeakerSegment, TranscriptSegment

def test_verify_integrity_success(mock_audio: Path) -> None:
    """Verifies that matching SHA hashes complete validation successfully."""
    import hashlib
    content = mock_audio.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    # Should not raise exception
    AudioValidator.verify_integrity(str(mock_audio.resolve()), sha256)

def test_verify_integrity_mismatch(mock_audio: Path) -> None:
    """Verifies that mismatching hashes raise ChecksumMismatchError."""
    bad_hash = "wrongsha"
    with pytest.raises(ChecksumMismatchError):
        AudioValidator.verify_integrity(str(mock_audio.resolve()), bad_hash)

def test_validate_timelines_invalid_speaker_label() -> None:
    """Verifies coordinate checks flag warnings on invalid speaker formatting."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.wav",
        page_number=1,
        parser="Test",
        parser_version="1.0.0",
        source_element=DocumentElementType.OCR
    )
    
    # Use model_construct to bypass pydantic pattern validation on init
    sp = SpeakerSegment.model_construct(
        segment_id="S1",
        speaker_label="Speaker_A",
        start_time=0.5,
        end_time=3.0,
        confidence=0.99,
        source_reference=ref
    )
    
    validation = AudioValidator.validate_timelines([sp], [])
    assert validation.integrity_status == "FAIL"
    assert len(validation.errors) == 1
