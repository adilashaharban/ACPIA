# -*- coding: utf-8 -*-
"""Vision RAG extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.rag.schema import ChunkType

class VisionExtractor:
    """Harvests raw labels and EXIF tags from vision intelligence outputs."""
    
    @staticmethod
    def extract(vision_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        extracted = []
        if not vision_payload:
            return extracted
            
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="VisionExtractor",
            parser_version="1.0.0",
            source_element=DocumentElementType.OCR
        )
        
        # Aggregate tags
        exif = vision_payload.get("exif", {})
        exif_str = ", ".join(f"{k}={v}" for k, v in exif.items())
        
        objects = vision_payload.get("objects", [])
        obj_names = ", ".join(o.get("label", "") for o in objects)
        
        desc = f"Image tags: {exif_str}. Detected objects: {obj_names}."
        
        extracted.append({
            "text": desc,
            "chunk_type": ChunkType.IMAGE,
            "source_reference": ref,
            "entity_ids": [],
            "timeline_event_ids": [],
            "graph_node_ids": [],
            "graph_edge_ids": [],
            "correlation_cluster_ids": []
        })
        return extracted
export_vision_extractor = VisionExtractor
