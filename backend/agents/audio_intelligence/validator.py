# -*- coding: utf-8 -*-
"""Audio validator module."""

import hashlib
import re
from pathlib import Path
from typing import List
from backend.agents.audio_intelligence.exceptions import ChecksumMismatchError, AudioParsingError
from backend.agents.audio_intelligence.schema import AudioValidation, SpeakerSegment, TranscriptSegment

class AudioValidator:
    """Validates acoustic signals and database checksums integrity."""
    
    _SPEAKER_LABEL_REGEX = re.compile(r"^Speaker_\d+$")

    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies file hashes match ingestion checksums.
        
        Args:
            file_path: Physical file path.
            expected_sha256: Ingestion hash.
            
        Raises:
            ChecksumMismatchError: If hashes differ.
            AudioParsingError: If file is missing or unreadable.
        """
        path = Path(file_path)
        if not path.exists():
            raise AudioParsingError(f"Target audio missing at verification path: {file_path}")
            
        try:
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            calculated = hasher.hexdigest()
            
            if calculated != expected_sha256:
                raise ChecksumMismatchError(
                    f"Integrity check failed. Expected: {expected_sha256}, Got: {calculated}",
                    details={"file_path": file_path, "expected": expected_sha256, "calculated": calculated}
                )
        except ChecksumMismatchError:
            raise
        except Exception as e:
            raise AudioParsingError(f"Integrity check processing crash: {e}")

    @classmethod
    def validate_timelines(
        cls, 
        speakers: List[SpeakerSegment], 
        segments: List[TranscriptSegment]
    ) -> AudioValidation:
        """Sanity checks start/end timestamps and Speaker_N label formats.
        
        Args:
            speakers: Diarization speaker segments.
            segments: Transcription segments.
            
        Returns:
            AudioValidation object.
        """
        warnings = []
        errors = []
        
        # Check speakers
        for sp in speakers:
            if sp.start_time > sp.end_time:
                errors.append(f"Invalid timeline range in speaker segment: {sp.start_time} > {sp.end_time}")
            if not cls._SPEAKER_LABEL_REGEX.match(sp.speaker_label):
                errors.append(f"Speaker label '{sp.speaker_label}' does not conform to Speaker_N format.")
                
        # Check segments
        for seg in segments:
            if seg.start_time > seg.end_time:
                errors.append(f"Invalid timeline range in transcript segment: {seg.start_time} > {seg.end_time}")
            if not cls._SPEAKER_LABEL_REGEX.match(seg.speaker_label):
                errors.append(f"Speaker label '{seg.speaker_label}' does not conform to Speaker_N format.")
                
        return AudioValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
export_validator = AudioValidator
