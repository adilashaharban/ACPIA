# -*- coding: utf-8 -*-
"""Vision observations extractor."""

import dateutil.parser
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType

class VisionExtractor:
    """Extracts candidate timestamps from Vision EXIF payloads."""
    
    @staticmethod
    def extract(vision_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateObservation]:
        candidates = []
        if not vision_payload:
            return candidates
            
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="VisionExtractor",
            parser_version="1.0.0",
            source_element=DocumentElementType.OCR
        )
        
        exif = vision_payload.get("exif", {})
        if exif:
            capture_date = exif.get("DateTimeOriginal") or exif.get("DateTime")
            if capture_date:
                try:
                    dt = dateutil.parser.parse(capture_date)
                except:
                    dt = None
                    
                candidates.append(
                    CandidateObservation(
                        candidate_id=f"CD-VIS-EXF-{evidence_id}",
                        observation_type=CorrelationType.TEMPORAL_MATCH,
                        originating_agent="vision_intelligence_agent",
                        evidence_id=evidence_id,
                        raw_value=capture_date,
                        normalized_value=capture_date,
                        confidence=0.95,
                        timestamp=dt,
                        source_reference=ref
                    )
                )
                
        return candidates
export_vision_extractor = VisionExtractor
