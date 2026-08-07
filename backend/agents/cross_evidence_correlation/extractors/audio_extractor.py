# -*- coding: utf-8 -*-
"""Audio observations extractor."""

import dateutil.parser
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType

class AudioExtractor:
    """Extracts candidate timestamps from Audio media metadata."""
    
    @staticmethod
    def extract(audio_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateObservation]:
        candidates = []
        if not audio_payload:
            return candidates
            
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="AudioExtractor",
            parser_version="1.0.0",
            source_element=DocumentElementType.OCR
        )
        
        media_info = audio_payload.get("media_info", {})
        if media_info:
            rec_date = media_info.get("creation_time")
            if rec_date:
                try:
                    dt = dateutil.parser.parse(rec_date)
                except:
                    dt = None
                    
                candidates.append(
                    CandidateObservation(
                        candidate_id=f"CD-AUD-REC-{evidence_id}",
                        observation_type=CorrelationType.TEMPORAL_MATCH,
                        originating_agent="audio_intelligence_agent",
                        evidence_id=evidence_id,
                        raw_value=rec_date,
                        normalized_value=rec_date,
                        confidence=0.96,
                        timestamp=dt,
                        source_reference=ref
                    )
                )
                
        return candidates
export_audio_extractor = AudioExtractor
