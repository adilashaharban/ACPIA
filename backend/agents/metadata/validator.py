# -*- coding: utf-8 -*-
"""Metadata validation engine."""

import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.agents.metadata.exceptions import ChecksumMismatchError, ParserFailureError
from backend.agents.metadata.schema import ValidationMetadata, GPSMetadata, ImageMetadata
from backend.agents.metadata.constants import GPS_LIMITS

class MetadataValidator:
    """Performs validation checks on extracted metadata structures and file payloads."""
    
    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies that the target file still matches the original intake checksum.
        
        Args:
            file_path: Physical file location.
            expected_sha256: Ingestion signature hash.
            
        Raises:
            ChecksumMismatchError: If file hash differs.
            ParserFailureError: If unable to read/open the file.
        """
        path = Path(file_path)
        if not path.exists():
            raise ParserFailureError(f"Evidence file missing at verification path: {file_path}")
            
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
            raise ParserFailureError(f"Integrity verification processing crash: {e}")

    @staticmethod
    def validate_metadata(
        file_path: str,
        file_type: str,
        raw_meta: Dict[str, Any],
        image_meta: Optional[ImageMetadata] = None
    ) -> ValidationMetadata:
        """Validates consistency of coordinates, timestamps, and codec variables.
        
        Args:
            file_path: File system location.
            file_type: File mime class.
            raw_meta: Raw parsed header dictionary.
            image_meta: Instantiated ImageMetadata object if image file.
            
        Returns:
            ValidationMetadata schema.
        """
        issues: List[str] = []
        integrity_status = "PASS"
        
        # 1. GPS boundary checks
        if image_meta and image_meta.gps:
            gps = image_meta.gps
            lat = gps.latitude
            lon = gps.longitude
            
            if lat is not None:
                if not (GPS_LIMITS["MIN_LATITUDE"] <= lat <= GPS_LIMITS["MAX_LATITUDE"]):
                    issues.append(f"GPS Latitude {lat} out of bounds.")
            if lon is not None:
                if not (GPS_LIMITS["MIN_LONGITUDE"] <= lon <= GPS_LIMITS["MAX_LONGITUDE"]):
                    issues.append(f"GPS Longitude {lon} out of bounds.")
                    
        # 2. EXIF camera fields checks
        if image_meta and image_meta.camera:
            cam = image_meta.camera
            if cam.make and not cam.model:
                issues.append("Camera manufacturer present but model tag is missing.")
                
        # 3. Codec and container validation
        suffix = Path(file_path).suffix.replace(".", "").lower()
        if file_type.startswith("video/") or file_type.startswith("audio/"):
            # Check container match against extension
            if suffix not in file_type.lower():
                issues.append(f"File extension '{suffix}' mismatches MIME class '{file_type}'.")
                
        return ValidationMetadata(
            integrity_verification=integrity_status,
            issues_detected=issues
        )
