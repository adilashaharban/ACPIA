# -*- coding: utf-8 -*-
"""Unit tests for StructuredParser."""

from backend.agents.investigation_reasoning.structured_parser import StructuredParser

def test_structured_parser() -> None:
    """Verifies findings lists extraction."""
    data = {
        "findings": [{"title": "F1"}],
        "contradictions": [{"description": "C1"}],
        "evidence_gaps": [{"description": "G1"}]
    }
    
    findings, contras, gaps = StructuredParser.parse_findings(data)
    assert len(findings) == 1
    assert len(contras) == 1
    assert len(gaps) == 1
