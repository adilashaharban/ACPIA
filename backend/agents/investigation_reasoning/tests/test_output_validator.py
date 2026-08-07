# -*- coding: utf-8 -*-
"""Unit tests for OutputValidator."""

import pytest
from backend.agents.investigation_reasoning.output_validator import OutputValidator
from backend.agents.investigation_reasoning.exceptions import ValidationError

def test_output_validator_success() -> None:
    """Verifies that valid json passes validations."""
    raw = '{"findings": []}'
    data = OutputValidator.validate_raw_json(raw)
    assert "findings" in data

def test_output_validator_invalid_json() -> None:
    """Verifies that invalid json raises ValidationError."""
    raw = '{"findings": '
    with pytest.raises(ValidationError):
        OutputValidator.validate_raw_json(raw)

def test_output_validator_missing_required() -> None:
    """Verifies that missing findings key raises ValidationError."""
    raw = '{"gaps": []}'
    with pytest.raises(ValidationError):
        OutputValidator.validate_raw_json(raw)
