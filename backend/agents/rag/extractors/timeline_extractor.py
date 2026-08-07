# -*- coding: utf-8 -*-
"""Timeline RAG extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.rag.schema import ChunkType

class TimelineExtractor:
    """Harvests parsed events list from timeline outputs."""
    
    @staticmethod
    def extract(timeline_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        extracted = []
        if not timeline_payload:
            return extracted
            
        events = timeline_payload.get("events", [])
        for ev in events:
            ev_id = ev.get("event_id")
            title = ev.get("title")
            norm_ts = ev.get("normalized_timestamp_utc")
            
            txt = f"Timeline Event {ev_id} on {norm_ts} titled: '{title}'."
            
            refs = ev.get("source_references", [])
            if refs:
                ref = SourceReference.model_validate(refs[0])
            else:
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=1,
                    parser="TimelineExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                
            extracted.append({
                "text": txt,
                "chunk_type": ChunkType.TIMELINE,
                "source_reference": ref,
                "entity_ids": [],
                "timeline_event_ids": [ev_id],
                "graph_node_ids": [],
                "graph_edge_ids": [],
                "correlation_cluster_ids": []
            })
        return extracted
export_timeline_extractor = TimelineExtractor
