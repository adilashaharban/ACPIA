# -*- coding: utf-8 -*-
"""Correlation validator module."""

import hashlib
from pathlib import Path
from typing import List
from backend.agents.cross_evidence_correlation.exceptions import ChecksumMismatchError, CorrelationError
from backend.agents.cross_evidence_correlation.schema import (
    CorrelationValidation, CorrelationCluster, CorrelationMatch, CorrelationConflict
)

class Validator:
    """Validates structural integrity, missing references, and bounding values."""
    
    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies evidence checksum.
        
        Args:
            file_path: Evidence file path.
            expected_sha256: Expected SHA hash.
        """
        path = Path(file_path)
        if not path.exists():
            raise CorrelationError(f"Evidence file missing during correlation verification: {file_path}")
            
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
            raise CorrelationError(f"Integrity check processing crash: {e}")

    @staticmethod
    def validate_package(
        clusters: List[CorrelationCluster],
        conflicts: List[CorrelationConflict]
    ) -> CorrelationValidation:
        """Runs validation checks.
        
        Args:
            clusters: Formed clusters.
            conflicts: Detected conflicts warnings.
            
        Returns:
            CorrelationValidation status check object.
        """
        warnings = []
        errors = []
        
        # 1. Check unique cluster IDs
        c_ids = [c.cluster_id for c in clusters]
        if len(c_ids) != len(set(c_ids)):
            errors.append("Duplicate cluster IDs detected in CorrelationClusters list.")
            
        # 2. Check unique match IDs inside clusters
        m_ids = []
        for c in clusters:
            m_ids.extend([m.match_id for m in c.correlations])
            
        if len(m_ids) != len(set(m_ids)):
            warnings.append("Duplicate correlation match IDs referenced across clusters.")
            
        # 3. Check invalid confidences
        for c in clusters:
            if not (0.0 <= c.confidence <= 1.0):
                errors.append(f"Cluster '{c.cluster_id}' confidence is outside bounds: {c.confidence}")
                
        return CorrelationValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
export_validator = Validator
