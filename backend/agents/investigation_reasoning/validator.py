# -*- coding: utf-8 -*-
"""Reasoning validator module."""

import hashlib
from pathlib import Path
from typing import List
from backend.agents.investigation_reasoning.exceptions import ChecksumMismatchError, ValidationError
from backend.agents.investigation_reasoning.schema import (
    ReasoningValidation, Finding, Contradiction
)

class Validator:
    """Validates structural package bounds and integrity validations."""
    
    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies evidence checksum.
        
        Args:
            file_path: Evidence file path.
            expected_sha256: Expected SHA hash.
        """
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"Evidence file missing during reasoning validation: {file_path}")
            
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
            raise ValidationError(f"Integrity check processing crash: {e}")

    @staticmethod
    def validate_package(
        findings: List[Finding],
        contradictions: List[Contradiction]
    ) -> ReasoningValidation:
        """Runs validation checks.
        
        Args:
            findings: Findings list.
            contradictions: Contradictions warnings.
            
        Returns:
            ReasoningValidation status check object.
        """
        warnings = []
        errors = []
        
        # Check unique finding IDs
        f_ids = [f.finding_id for f in findings]
        if len(f_ids) != len(set(f_ids)):
            errors.append("Duplicate finding IDs detected in ReasoningPackage.")
            
        # Check invalid confidences
        for f in findings:
            if not (0.0 <= f.confidence.final_score <= 1.0):
                errors.append(f"Finding '{f.finding_id}' final_confidence score outside bounds: {f.confidence.final_score}")
                
        return ReasoningValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
export_validator = Validator
