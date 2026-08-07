# -*- coding: utf-8 -*-
"""Entity resolution normalizer."""

import re
import phonenumbers
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType

class EntityNormalizer:
    """Standardizes string values to enable exact matching checks across formats."""
    
    @staticmethod
    def normalize_email(val: str) -> str:
        """Converts emails to canonical lowercase format.
        
        Args:
            val: Raw string.
            
        Returns:
            Lowercase string.
        """
        return val.strip().lower()

    @staticmethod
    def normalize_phone(val: str) -> str:
        """Formats phone values to standard E.164.
        
        Args:
            val: Raw string.
            
        Returns:
            E.164 formatted string or cleaned original if parsing fails.
        """
        try:
            # Parse assuming standard IN/US defaults if country prefix is absent
            parsed = phonenumbers.parse(val, "IN")
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            pass
        # Fallback to digits extraction only
        return "+" + "".join(re.findall(r"\d+", val))

    @staticmethod
    def normalize_generic(val: str) -> str:
        """Strips surrounding spaces and normalizes character spaces.
        
        Args:
            val: Raw string.
            
        Returns:
            Normalized string.
        """
        if not val:
            return ""
        return re.sub(r"\s+", " ", val).strip()

    @classmethod
    def normalize_candidate(cls, candidate: CandidateEntity) -> CandidateEntity:
        """Standardizes values inside CandidateEntity pools.
        
        Args:
            candidate: Raw CandidateEntity.
            
        Returns:
            A new normalized CandidateEntity.
        """
        raw = candidate.raw_value
        norm_val = raw
        
        if candidate.entity_type == EntityType.EMAIL:
            norm_val = cls.normalize_email(raw)
        elif candidate.entity_type == EntityType.PHONE:
            norm_val = cls.normalize_phone(raw)
        else:
            norm_val = cls.normalize_generic(raw)
            
        return CandidateEntity(
            candidate_id=candidate.candidate_id,
            entity_type=candidate.entity_type,
            raw_value=raw,
            normalized_value=norm_val,
            confidence=candidate.confidence,
            extraction_agent=candidate.extraction_agent,
            source_reference=candidate.source_reference,
            supporting_attributes=candidate.supporting_attributes
        )
