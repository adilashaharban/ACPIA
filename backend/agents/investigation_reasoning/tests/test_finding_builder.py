# -*- coding: utf-8 -*-
"""Unit tests for FindingBuilder."""

from backend.agents.investigation_reasoning.finding_builder import FindingBuilder
from backend.agents.investigation_reasoning.schema import FindingType, FindingStatus

def test_finding_builder() -> None:
    """Verifies that findings parameters compile properly."""
    raw = {
        "finding_id": "FND-1",
        "title": "Claim Title",
        "description": "Details description",
        "finding_type": "CONCLUSION",
        "finding_status": "CONTRADICTED"
    }
    
    f = FindingBuilder.build_finding(raw)
    assert f.finding_id == "FND-1"
    assert f.finding_type == FindingType.CONCLUSION
    assert f.finding_status == FindingStatus.CONTRADICTED
