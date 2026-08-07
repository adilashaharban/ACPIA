# -*- coding: utf-8 -*-
"""Document timeline events extractor."""

import re
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.timeline_intelligence.schema import TimelineEventType

class DocumentExtractor:
    """Scans parsed page segments for message patterns or date-bearing text strings."""
    
    # Matches ISO datetimes or date strings in document body text
    _DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}\b")

    @classmethod
    def extract(cls, doc_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        candidates = []
        if not doc_payload:
            return candidates
            
        structure = doc_payload.get("structure", {})
        pages = structure.get("pages", [])
        
        for page in pages:
            page_num = page.get("page_number", 1)
            text = page.get("text_content", "")
            
            # Find datetimes in text
            matches = cls._DATE_PATTERN.findall(text)
            for raw_date in matches:
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="DocumentExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                candidates.append({
                    "event_type": TimelineEventType.DOCUMENT_EDITED,
                    "title": "Document Edited Mentions",
                    "description": f"Observed timestamp inside page content: {raw_date}",
                    "raw_timestamp": raw_date,
                    "confidence": 0.90,
                    "source_reference": ref,
                    "location": None,
                    "artifacts": []
                })
                
        return candidates
export_doc_extractor = DocumentExtractor
