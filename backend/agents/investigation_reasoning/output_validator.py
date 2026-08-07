# -*- coding: utf-8 -*-
"""Output json validator module."""

import json
from typing import Dict, Any
from backend.agents.investigation_reasoning.exceptions import ValidationError

class OutputValidator:
    """Pre-validates LLM JSON output structure prior to full parsing."""
    
    @staticmethod
    def validate_raw_json(raw_text: str) -> Dict[str, Any]:
        """Checks valid JSON syntax and parses to dict.
        
        Args:
            raw_text: LLM string output.
            
        Returns:
            Decoded dictionary.
        """
        try:
            data = json.loads(raw_text)
        except Exception as e:
            raise ValidationError(f"Invalid JSON response returned from LLM provider: {e}")
            
        if not isinstance(data, dict):
            raise ValidationError("Decoded LLM output is not a JSON dictionary.")
            
        # Check required fields
        if "findings" not in data:
            raise ValidationError("Missing required output field: 'findings'.")
            
        return data
export_output_validator = OutputValidator
