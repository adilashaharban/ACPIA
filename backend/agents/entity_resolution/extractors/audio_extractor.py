# -*- coding: utf-8 -*-
"""Audio agent candidate entity extractor."""

import uuid
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType

class AudioExtractor:
    """Extracts candidate entities from transcribed keywords and segments."""
    
    @staticmethod
    def extract(audio_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateEntity]:
        candidates: List[CandidateEntity] = []
        if not audio_payload:
            return candidates
            
        # Extract keywords spotted
        keywords = audio_payload.get("keywords", [])
        for kw in keywords:
            ref = SourceReference(
                evidence_id=evidence_id,
                file_path=file_path,
                page_number=1,
                parser="AudioExtractor",
                parser_version="1.0.0",
                source_element=DocumentElementType.OCR
            )
            candidates.append(
                CandidateEntity(
                    candidate_id=str(uuid.uuid4()),
                    entity_type=EntityType.UNKNOWN,
                    raw_value=kw.get("keyword", ""),
                    normalized_value=kw.get("keyword", ""),
                    confidence=kw.get("confidence", 0.90),
                    extraction_agent="audio_intelligence",
                    source_reference=ref
                )
            )
            
        return candidates
export_audio_extractor = AudioExtractor
