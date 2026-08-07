# -*- coding: utf-8 -*-
"""Document text candidate entity extractor."""

import re
import uuid
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType

class DocumentExtractor:
    """Extracts candidate entities from parsed text blocks using regular expressions."""
    
    # Regular expressions for entity sweeps
    _EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    _PHONE_REGEX = re.compile(r"\+?\d{1,4}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}")
    _URL_REGEX = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")

    @classmethod
    def extract(cls, doc_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateEntity]:
        candidates: List[CandidateEntity] = []
        if not doc_payload:
            return candidates
            
        # Traverse paragraphs inside page structures
        structure = doc_payload.get("structure", {})
        pages = structure.get("pages", [])
        
        for page in pages:
            page_num = page.get("page_number", 1)
            text_content = page.get("text_content", "")
            
            # Find emails
            for email in cls._EMAIL_REGEX.findall(text_content):
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="DocumentExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                candidates.append(
                    CandidateEntity(
                        candidate_id=str(uuid.uuid4()),
                        entity_type=EntityType.EMAIL,
                        raw_value=email,
                        normalized_value=email,
                        confidence=0.95,
                        extraction_agent="document_intelligence",
                        source_reference=ref
                    )
                )
                
            # Find phones
            for phone in cls._PHONE_REGEX.findall(text_content):
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="DocumentExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                candidates.append(
                    CandidateEntity(
                        candidate_id=str(uuid.uuid4()),
                        entity_type=EntityType.PHONE,
                        raw_value=phone,
                        normalized_value=phone,
                        confidence=0.90,
                        extraction_agent="document_intelligence",
                        source_reference=ref
                    )
                )
                
            # Find URLs
            for url in cls._URL_REGEX.findall(text_content):
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="DocumentExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                candidates.append(
                    CandidateEntity(
                        candidate_id=str(uuid.uuid4()),
                        entity_type=EntityType.URL,
                        raw_value=url,
                        normalized_value=url,
                        confidence=0.92,
                        extraction_agent="document_intelligence",
                        source_reference=ref
                    )
                )
                
        return candidates
export_doc_extractor = DocumentExtractor
