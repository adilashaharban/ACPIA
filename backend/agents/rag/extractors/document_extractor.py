# -*- coding: utf-8 -*-
"""Document RAG extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.rag.schema import ChunkType

class DocumentExtractor:
    """Harvests raw page texts from document intelligence outputs."""
    
    @staticmethod
    def extract(doc_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        extracted = []
        if not doc_payload:
            return extracted
            
        structure = doc_payload.get("structure", {})
        pages = structure.get("pages", [])
        
        for page in pages:
            page_num = page.get("page_number", 1)
            text = page.get("text_content", "")
            if not text.strip():
                continue
                
            ref = SourceReference(
                evidence_id=evidence_id,
                file_path=file_path,
                page_number=page_num,
                parser="DocumentExtractor",
                parser_version="1.0.0",
                source_element=DocumentElementType.PARAGRAPH
            )
            
            extracted.append({
                "text": text,
                "chunk_type": ChunkType.DOCUMENT,
                "source_reference": ref,
                "entity_ids": [],
                "timeline_event_ids": [],
                "graph_node_ids": [],
                "graph_edge_ids": [],
                "correlation_cluster_ids": []
            })
        return extracted
export_doc_extractor = DocumentExtractor
