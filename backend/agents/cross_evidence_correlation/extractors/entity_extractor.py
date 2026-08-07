# -*- coding: utf-8 -*-
"""Entity observations extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType

class EntityExtractor:
    """Harvests resolved canonical entity items from EntityResolutionPackage."""
    
    @staticmethod
    def extract(entity_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateObservation]:
        candidates = []
        if not entity_payload:
            return candidates
            
        entities = entity_payload.get("entities", [])
        for ent in entities:
            ent_id = ent.get("entity_id")
            name = ent.get("canonical_name")
            e_type = ent.get("entity_type")
            confidence = ent.get("confidence_breakdown", {}).get("final_confidence", 0.90)
            
            # Use first source reference if available
            refs = ent.get("source_references", [])
            if refs:
                ref = SourceReference.model_validate(refs[0])
            else:
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=1,
                    parser="EntityExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                
            candidates.append(
                CandidateObservation(
                    candidate_id=f"CD-ENT-{ent_id}",
                    observation_type=CorrelationType.ENTITY_MATCH,
                    originating_agent="entity_resolution_agent",
                    evidence_id=evidence_id,
                    raw_value=name,
                    normalized_value=name.lower().strip(),
                    confidence=confidence,
                    entity_id=ent_id,
                    source_reference=ref
                )
            )
            
        return candidates
export_entity_extractor = EntityExtractor
