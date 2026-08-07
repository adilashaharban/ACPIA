# -*- coding: utf-8 -*-
"""Entity validation module."""

import hashlib
import re
from pathlib import Path
from typing import List
from backend.agents.entity_resolution.exceptions import ChecksumMismatchError, ResolutionParsingError
from backend.agents.entity_resolution.schema import EntityValidation, CanonicalEntity, EntityType

class EntityValidator:
    """Validates structural entity attributes and integrity checks."""
    
    _EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    _PHONE_E164_REGEX = re.compile(r"^\+\d{10,15}$")

    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies file hash values.
        
        Args:
            file_path: File path.
            expected_sha256: Ingestion hash.
        """
        path = Path(file_path)
        if not path.exists():
            raise ResolutionParsingError(f"Evidence file missing at verification: {file_path}")
            
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
            raise ResolutionParsingError(f"Integrity check processing crash: {e}")

    @classmethod
    def validate_entities(cls, entities: List[CanonicalEntity]) -> EntityValidation:
        """Validates canonical elements structure.
        
        Args:
            entities: Resolved entities.
            
        Returns:
            EntityValidation object.
        """
        warnings = []
        errors = []
        
        # Check duplicate entity IDs
        entity_ids = [e.entity_id for e in entities]
        if len(entity_ids) != len(set(entity_ids)):
            errors.append("Duplicate entity IDs detected inside resolved pool.")
            
        for entity in entities:
            # Check emails formats
            if entity.entity_type == EntityType.EMAIL:
                if not cls._EMAIL_REGEX.match(entity.canonical_name):
                    warnings.append(f"Email '{entity.canonical_name}' does not match standard patterns.")
            # Check phone E.164 formats
            elif entity.entity_type == EntityType.PHONE:
                if not cls._PHONE_E164_REGEX.match(entity.canonical_name):
                    warnings.append(f"Phone '{entity.canonical_name}' does not match E.164 formatting.")
                    
        return EntityValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
