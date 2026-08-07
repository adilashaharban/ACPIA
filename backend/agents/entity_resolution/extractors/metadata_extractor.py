# -*- coding: utf-8 -*-
"""Metadata agent candidate entity extractor."""

import uuid
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType

class MetadataExtractor:
    """Extracts candidate entities from file specs and system logs metadata."""
    
    @staticmethod
    def extract(metadata_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateEntity]:
        candidates: List[CandidateEntity] = []
        if not metadata_payload:
            return candidates
            
        # Extract system File candidate
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="MetadataExtractor",
            parser_version="1.0.0",
            source_element=DocumentElementType.PARAGRAPH
        )
        
        file_specs = metadata_payload.get("file_specs", {})
        if file_specs:
            candidates.append(
                CandidateEntity(
                    candidate_id=str(uuid.uuid4()),
                    entity_type=EntityType.FILE,
                    raw_value=file_path,
                    normalized_value=file_path,
                    confidence=1.0,
                    extraction_agent="metadata_agent",
                    source_reference=ref,
                    supporting_attributes=[]
                )
            )
            
        return candidates
export_meta_extractor = MetadataExtractor
