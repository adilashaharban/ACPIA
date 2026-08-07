# -*- coding: utf-8 -*-
"""Unit tests for ContradictionDetector."""

from backend.agents.investigation_reasoning.contradiction_detector import ContradictionDetector
from backend.agents.investigation_reasoning.schema import Finding, FindingType, FindingStatus, ReasoningConfidence

def test_contradiction_detector() -> None:
    """Verifies that opposing claims on identical evidence items generate contradictions."""
    conf = ReasoningConfidence(
        evidence_score=0.90, retrieval_score=0.90, citation_score=0.90,
        consistency_score=1.0, model_score=0.90, final_score=0.92
    )
    
    f1 = Finding(
        finding_id="F1",
        title="Claim 1",
        description="Factual observations",
        finding_type=FindingType.FACTUAL_OBSERVATION,
        finding_status=FindingStatus.SUPPORTED,
        confidence=conf,
        supporting_evidence_ids=["EVID-1"]
    )
    
    f2 = Finding(
        finding_id="F2",
        title="Claim 2",
        description="Inconsistent details",
        finding_type=FindingType.INCONSISTENCY,
        finding_status=FindingStatus.CONTRADICTED,
        confidence=conf,
        supporting_evidence_ids=["EVID-1"]
    )
    
    contras = ContradictionDetector.detect_contradictions([f1, f2])
    assert len(contras) == 1
    assert "F1" in contras[0].conflicting_finding_ids
