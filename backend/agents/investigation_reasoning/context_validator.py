# -*- coding: utf-8 -*-
"""Retrieval context validator module."""

from backend.agents.investigation_reasoning.exceptions import ValidationError
from backend.agents.rag.schema import RetrievalPackage

class ContextValidator:
    """Verifies that the RAG retrieval context is valid and not empty."""
    
    @staticmethod
    def validate(package: RetrievalPackage) -> None:
        """Verifies package properties.
        
        Args:
            package: Incoming RetrievalPackage.
        """
        if not package:
            raise ValidationError("RetrievalPackage context is empty or missing.")
            
        if not package.context:
            raise ValidationError("RetrievalPackage does not contain a consolidated context text block.")
            
        if not package.context.context_text.strip():
            raise ValidationError("RetrievalPackage context_text is blank.")
export_context_validator = ContextValidator
