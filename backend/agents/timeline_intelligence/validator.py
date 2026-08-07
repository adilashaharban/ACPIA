# -*- coding: utf-8 -*-
"""Timeline validator module."""

import hashlib
from pathlib import Path
from typing import List
from backend.agents.timeline_intelligence.exceptions import ChecksumMismatchError, TimelineException
from backend.agents.timeline_intelligence.schema import TimelineValidation, TimelineEvent

class TimelineValidator:
    """Checks sequence constraints and missing event source provenance details."""
    
    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies file checksum.
        
        Args:
            file_path: Evidence file path.
            expected_sha256: Expected SHA hash.
        """
        path = Path(file_path)
        if not path.exists():
            raise TimelineException(f"Evidence file missing during timeline verification: {file_path}")
            
        try:
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            calculated = hasher.hexdigest()
            if calculated != expected_sha256:
                raise ChecksumMismatchError(
                    f"Integrity check failed. Expected: {expected_sha256}, Got: {calculated}"
                )
        except ChecksumMismatchError:
            raise
        except Exception as e:
            raise TimelineException(f"Integrity check processing crash: {e}")

    @staticmethod
    def validate_timeline(events: List[TimelineEvent]) -> TimelineValidation:
        """Sanity checks event order and provenance.
        
        Args:
            events: List of sorted events.
            
        Returns:
            TimelineValidation object.
        """
        warnings = []
        errors = []
        
        # 1. Check chronological order consistency
        for idx in range(1, len(events)):
            prev = events[idx - 1]
            curr = events[idx]
            if curr.normalized_timestamp_utc < prev.normalized_timestamp_utc:
                errors.append(f"Timeline sorting constraint broken: Event {curr.event_id} occurred before {prev.event_id}.")
                
        # 2. Check duplicate IDs
        event_ids = [e.event_id for e in events]
        if len(event_ids) != len(set(event_ids)):
            errors.append("Duplicate event IDs detected inside timeline package.")
            
        # 3. Check UTC normalizations
        for e in events:
            if e.normalized_timestamp_utc.tzinfo is None:
                errors.append(f"Event {e.event_id} has naive datetime object.")
            if not e.origin.agent_name:
                warnings.append(f"Event {e.event_id} is missing origin agent provenance description.")
                
        return TimelineValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
export_validator = TimelineValidator
