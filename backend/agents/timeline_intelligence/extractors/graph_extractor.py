# -*- coding: utf-8 -*-
"""Graph timeline events extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.timeline_intelligence.schema import TimelineEventType

class GraphExtractor:
    """Harvests observed node timestamps directly from the Knowledge Graph."""
    
    @staticmethod
    def extract(graph_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        candidates = []
        if not graph_payload:
            return candidates
            
        nodes = graph_payload.get("nodes", [])
        for node in nodes:
            node_id = node.get("node_id")
            node_type = node.get("node_type")
            properties = node.get("properties", [])
            
            # Search properties for time keys
            for prop in properties:
                key = prop.get("key")
                val = prop.get("value")
                
                # Check keys representing timestamps
                if key in ["timestamp", "created_at", "occurred_at"] and val:
                    # Resolve TimelineEventType from NodeType
                    event_type = TimelineEventType.UNKNOWN
                    if node_type == "LOCATION":
                        event_type = TimelineEventType.LOCATION_OBSERVED
                    elif node_type == "EVENT":
                        event_type = TimelineEventType.DEVICE_USED
                        
                    # Locate source ref
                    source_ref_dict = prop.get("source_reference")
                    if source_ref_dict:
                        ref = SourceReference.model_validate(source_ref_dict)
                    else:
                        ref = SourceReference(
                            evidence_id=evidence_id,
                            file_path=file_path,
                            page_number=1,
                            parser="GraphExtractor",
                            parser_version="1.0.0",
                            source_element=DocumentElementType.PARAGRAPH
                        )
                        
                    candidates.append({
                        "event_type": event_type,
                        "title": f"Graph Node Observation: {node.get('label')}",
                        "description": f"Extracted temporal property: {key} = {val}",
                        "raw_timestamp": str(val),
                        "confidence": prop.get("confidence", 0.90),
                        "source_reference": ref,
                        "location": None,
                        "artifacts": [],
                        "graph_nodes": [node_id]
                    })
                    
        return candidates
export_graph_extractor = GraphExtractor
