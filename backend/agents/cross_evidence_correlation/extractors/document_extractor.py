# -*- coding: utf-8 -*-
"""Document observations extractor."""

import re
import dateutil.parser
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType

class DocumentExtractor:
    """Scans page content for date indicators."""
    
    _DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}\b")

    @classmethod
    def extract(cls, doc_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateObservation]:
        candidates = []
        if not doc_payload:
            return candidates
            
        structure = doc_payload.get("structure", {})
        pages = structure.get("pages", [])
        
        for page in pages:
            page_num = page.get("page_number", 1)
            text = page.get("text_content", "")
            
            matches = cls._DATE_PATTERN.findall(text)
            for idx, raw_date in enumerate(matches):
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="DocumentExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                try:
                    dt = dateutil.parser.parse(raw_date)
                except:
                    dt = None
                    
                candidates.append(
                    CandidateObservation(
                        candidate_id=f"CD-DOC-DATE-{evidence_id}-{page_num}-{idx}",
                        observation_type=CorrelationType.TEMPORAL_MATCH,
                        originating_agent="document_intelligence_agent",
                        evidence_id=evidence_id,
                        raw_value=raw_date,
                        normalized_value=raw_date,
                        confidence=0.90,
                        timestamp=dt,
                        source_reference=ref
                    )
                )
                
        return candidates
export_doc_extractor = DocumentExtractor
