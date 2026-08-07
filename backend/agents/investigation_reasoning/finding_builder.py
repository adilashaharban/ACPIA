# -*- coding: utf-8 -*-
"""Finding builder module."""

import uuid
from typing import Dict, Any, List
from backend.agents.investigation_reasoning.schema import (
    Finding, FindingType, FindingStatus, ReasoningConfidence, ReasoningStep
)

class FindingBuilder:
    """Assembles Finding schemas from raw parsed LLM findings fields."""
    
    @staticmethod
    def build_finding(raw: Dict[str, Any]) -> Finding:
        """Assembles a single Finding.
        
        Args:
            raw: Raw dict details.
            
        Returns:
            Pydantic Finding.
        """
        fid = raw.get("finding_id") or f"FND-{str(uuid.uuid4())[:8]}"
        title = raw.get("title") or "Unnamed Finding"
        desc = raw.get("description") or ""
        
        # Resolve type
        f_type_str = raw.get("finding_type") or "FACTUAL_OBSERVATION"
        try:
            finding_type = FindingType(f_type_str)
        except:
            finding_type = FindingType.FACTUAL_OBSERVATION
            
        # Resolve status
        f_status_str = raw.get("finding_status") or "SUPPORTED"
        try:
            finding_status = FindingStatus(f_status_str)
        except:
            finding_status = FindingStatus.SUPPORTED
            
        # Initial confidence mock (confidence_calculator will aggregate scores)
        conf = ReasoningConfidence(
            evidence_score=0.90,
            retrieval_score=0.90,
            citation_score=0.90,
            consistency_score=1.0,
            model_score=0.90,
            final_score=0.90
        )
        
        supporting_evidence = raw.get("supporting_evidence_ids", [])
        supporting_entities = raw.get("supporting_entities", [])
        
        return Finding(
            finding_id=fid,
            title=title,
            description=desc,
            finding_type=finding_type,
            finding_status=finding_status,
            confidence=conf,
            supporting_evidence_ids=supporting_evidence,
            supporting_entities=supporting_entities,
            supporting_graph_nodes=[],
            supporting_graph_edges=[],
            supporting_timeline_events=[],
            supporting_correlation_clusters=[],
            citations=[],
            reasoning_steps=[]
        )
export_finding_builder = FindingBuilder
