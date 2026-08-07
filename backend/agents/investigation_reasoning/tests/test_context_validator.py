# -*- coding: utf-8 -*-
"""Unit tests for ContextValidator."""

import pytest
from backend.agents.investigation_reasoning.context_validator import ContextValidator
from backend.agents.investigation_reasoning.exceptions import ValidationError
from backend.agents.rag.schema import RetrievalPackage

def test_context_validator_success(mock_retrieval_package: RetrievalPackage) -> None:
    """Verifies that complete RetrievalPackage passes."""
    ContextValidator.validate(mock_retrieval_package)

def test_context_validator_empty() -> None:
    """Verifies that empty RAG context raises ValidationError."""
    with pytest.raises(ValidationError):
        ContextValidator.validate(None)
