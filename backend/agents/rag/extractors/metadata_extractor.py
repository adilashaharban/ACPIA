# -*- coding: utf-8 -*-
"""Metadata RAG extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.rag.schema import ChunkType

class MetadataExtractor:
    """Harvests raw file characteristics details from metadata outputs."""
    
    @staticmethod
    def extract(metadata_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        extracted = []
        if not metadata_payload:
            return extracted
            
        file_specs = metadata_payload.get("file_specs", {})
        if not file_specs:
            return extracted
            
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="MetadataExtractor",
            parser_version="1.0.0",
            source_element=DocumentElementType.PARAGRAPH
        )
        
        # Build text description
        sz = file_specs.get("file_size_bytes", 0)
        c_time = file_specs.get("creation_time", "Unknown")
        m_time = file_specs.get("modification_time", "Unknown")
        txt = f"File {file_path} specs: size {sz} bytes, created at {c_time}, modified at {m_time}."
        
        extracted.append({
            "text": txt,
            "chunk_type": ChunkType.DOCUMENT,
            "source_reference": ref,
            "entity_ids": [],
            "timeline_event_ids": [],
            "graph_node_ids": [],
            "graph_edge_ids": [],
            "correlation_cluster_ids": []
        })
        return extracted
export_meta_extractor = MetadataExtractor
