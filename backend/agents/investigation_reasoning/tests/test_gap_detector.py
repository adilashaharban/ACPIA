# -*- coding: utf-8 -*-
"""Unit tests for GapDetector."""

from backend.agents.investigation_reasoning.gap_detector import GapDetector
from backend.agents.investigation_reasoning.schema import Finding, FindingType, FindingStatus, ReasoningConfidence

def test_gap_detector() -> None:
    """Verifies that findings lacking citations generate gaps."""
    conf = ReasoningConfidence(
        evidence_score=0.90, retrieval_score=0.90, citation_score=0.90,
        consistency_score=1.0, model_score=0.90, final_score=0.92
    )
    
    f = Finding(
        finding_id="F1",
        title="Claim 1",
        description="Factual observations",
        finding_type=FindingType.FACTUAL_OBSERVATION,
        finding_status=FindingStatus.SUPPORTED,
        confidence=conf,
        citations=[]
    )
    
    gaps = GapDetector.detect_gaps([f])
    assert len(gaps) == 1
    assert gaps[0].missing_evidence_type == "CITATION_CANDIDATE"
export_test_gap_detector = test_gap_detector
