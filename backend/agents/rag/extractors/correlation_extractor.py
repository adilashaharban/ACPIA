# -*- coding: utf-8 -*-
"""Correlation RAG extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.rag.schema import ChunkType

class CorrelationExtractor:
    """Harvests formed correlation clusters details from correlation agent outputs."""
    
    @staticmethod
    def extract(correlation_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        extracted = []
        if not correlation_payload:
            return extracted
            
        clusters = correlation_payload.get("clusters", [])
        for c in clusters:
            c_id = c.get("cluster_id")
            name = c.get("cluster_name")
            
            txt = f"Cross-Evidence Correlation Cluster {c_id} named: '{name}'."
            
            refs = c.get("source_references", [])
            if refs:
                ref = SourceReference.model_validate(refs[0])
            else:
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=1,
                    parser="CorrelationExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                
            extracted.append({
                "text": txt,
                "chunk_type": ChunkType.CORRELATION,
                "source_reference": ref,
                "entity_ids": [],
                "timeline_event_ids": [],
                "graph_node_ids": [],
                "graph_edge_ids": [],
                "correlation_cluster_ids": [c_id]
            })
        return extracted
export_correlation_extractor = CorrelationExtractor
