# -*- coding: utf-8 -*-
"""Contradiction detector module."""

import uuid
from typing import List, Dict, Any
from backend.agents.investigation_reasoning.schema import Contradiction, Finding, SeverityLevel

class ContradictionDetector:
    """Checks findings lists for opposing conclusions or statuses."""
    
    @staticmethod
    def detect_contradictions(findings: List[Finding]) -> List[Contradiction]:
        """Scans findings for logical inconsistencies.
        
        Args:
            findings: Findings list.
            
        Returns:
            Contradiction warnings list.
        """
        contradictions = []
        
        # Simple rule: If two findings exist with opposite statuses/conclusions
        for i in range(len(findings)):
            f1 = findings[i]
            for j in range(i + 1, len(findings)):
                f2 = findings[j]
                
                # Check for contradiction signature
                if f1.finding_type != f2.finding_type and f1.supporting_evidence_ids == f2.supporting_evidence_ids:
                    contradictions.append(
                        Contradiction(
                            contradiction_id=f"CFL-{str(uuid.uuid4())[:8]}",
                            description=f"Findings {f1.finding_id} and {f2.finding_id} claim opposing types on identical evidence references.",
                            conflicting_finding_ids=[f1.finding_id, f2.finding_id],
                            severity=SeverityLevel.HIGH
                        )
                    )
                    
        return contradictions
export_contradiction_detector = ContradictionDetector
