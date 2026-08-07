# -*- coding: utf-8 -*-
"""Vision validator module."""

import hashlib
from pathlib import Path
from typing import List
from backend.agents.vision_intelligence.exceptions import ChecksumMismatchError, VisionParsingError
from backend.agents.vision_intelligence.schema import VisionValidation, BoundingBox

class VisionValidator:
    """Validates graphic dimensions and integrity checksum matches."""
    
    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies visual file hash matches ingestion records.
        
        Args:
            file_path: Physical file path.
            expected_sha256: Target SHA-256 hash.
            
        Raises:
            ChecksumMismatchError: If hashes differ.
            VisionParsingError: If file is missing or unreadable.
        """
        path = Path(file_path)
        if not path.exists():
            raise VisionParsingError(f"Target graphic missing at verification path: {file_path}")
            
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
            raise VisionParsingError(f"Integrity check processing crash: {e}")

    @staticmethod
    def validate_detections(boxes: List[BoundingBox]) -> VisionValidation:
        """Sanity checks coordinate values to flag warning flags.
        
        Args:
            boxes: Bounding boxes to check.
            
        Returns:
            VisionValidation object.
        """
        warnings = []
        errors = []
        
        for box in boxes:
            if box.x0 > box.x1 or box.y0 > box.y1:
                errors.append(f"Invalid bounding box orientation detected: {box}")
                
        return VisionValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
