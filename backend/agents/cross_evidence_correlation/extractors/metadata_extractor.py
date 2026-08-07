# -*- coding: utf-8 -*-
"""Metadata observations extractor."""

import dateutil.parser
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType

class MetadataExtractor:
    """Extracts candidate timestamps from MetadataPackage payloads."""
    
    @staticmethod
    def extract(metadata_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateObservation]:
        candidates = []
        if not metadata_payload:
            return candidates
            
        file_specs = metadata_payload.get("file_specs", {})
        if not file_specs:
            return candidates
            
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="MetadataExtractor",
            parser_version="1.0.0",
            source_element=DocumentElementType.PARAGRAPH
        )
        
        creation_time = file_specs.get("creation_time")
        if creation_time:
            dt = dateutil.parser.parse(creation_time)
            candidates.append(
                CandidateObservation(
                    candidate_id=f"CD-MD-CRT-{evidence_id}",
                    observation_type=CorrelationType.TEMPORAL_MATCH,
                    originating_agent="metadata_agent",
                    evidence_id=evidence_id,
                    raw_value=creation_time,
                    normalized_value=creation_time,
                    confidence=1.0,
                    timestamp=dt,
                    source_reference=ref
                )
            )
            
        return candidates
export_meta_extractor = MetadataExtractor
