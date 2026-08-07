# -*- coding: utf-8 -*-
"""Evidence gap detector module."""

import uuid
from typing import List, Dict, Any
from backend.agents.investigation_reasoning.schema import EvidenceGap, Finding

class GapDetector:
    """Scans findings to verify missing timeline links or unresolved entities."""
    
    @staticmethod
    def detect_gaps(findings: List[Finding]) -> List[EvidenceGap]:
        """Flags missing evidence parameters.
        
        Args:
            findings: Findings list.
            
        Returns:
            EvidenceGap list.
        """
        gaps = []
        
        for f in findings:
            # Check for missing citations on unsupported observations
            if not f.citations:
                gaps.append(
                    EvidenceGap(
                        gap_id=f"GAP-{str(uuid.uuid4())[:8]}",
                        description=f"Finding {f.finding_id} lacks supporting citation sources.",
                        unresolved_entities=f.supporting_entities,
                        missing_evidence_type="CITATION_CANDIDATE"
                    )
                )
                
        return gaps
export_gap_detector = GapDetector
