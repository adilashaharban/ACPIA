# -*- coding: utf-8 -*-
"""Audio timeline events extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.timeline_intelligence.schema import TimelineEventType

class AudioExtractor:
    """Extracts candidate timestamps from call duration logs or recording headers."""
    
    @staticmethod
    def extract(audio_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
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
        
        # Audio recordings Exif or media info
        media_info = audio_payload.get("media_info", {})
        if media_info:
            rec_date = media_info.get("creation_time")
            if rec_date:
                candidates.append({
                    "event_type": TimelineEventType.AUDIO_RECORDED,
                    "title": "Audio Recorded",
                    "description": f"Audio track recording date: {rec_date}",
                    "raw_timestamp": rec_date,
                    "confidence": 0.96,
                    "source_reference": ref,
                    "location": None,
                    "artifacts": [{"evidence_id": evidence_id, "artifact_type": "AUDIO", "file_name": file_path}]
                })
                
        return candidates
export_audio_extractor = AudioExtractor
