# -*- coding: utf-8 -*-
"""Vision timeline events extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.timeline_intelligence.schema import TimelineEventType

class VisionExtractor:
    """Extracts candidate capture dates from EXIF logs or video frame references."""
    
    @staticmethod
    def extract(vision_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
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
        
        # Check for image capture EXIF tags
        exif = vision_payload.get("exif", {})
        if exif:
            capture_date = exif.get("DateTimeOriginal") or exif.get("DateTime")
            if capture_date:
                candidates.append({
                    "event_type": TimelineEventType.PHOTO_CAPTURED,
                    "title": "Photo Captured",
                    "description": f"Camera capture date registered: {capture_date}",
                    "raw_timestamp": capture_date,
                    "confidence": 0.95,
                    "source_reference": ref,
                    "location": None,
                    "artifacts": [{"evidence_id": evidence_id, "artifact_type": "IMAGE", "file_name": file_path}]
                })
                
        return candidates
export_vision_extractor = VisionExtractor
