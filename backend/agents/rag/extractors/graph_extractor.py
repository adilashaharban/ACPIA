# -*- coding: utf-8 -*-
"""Graph RAG extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.rag.schema import ChunkType

class GraphExtractor:
    """Harvests observed node descriptions from Knowledge Graph outputs."""
    
    @staticmethod
    def extract(graph_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        extracted = []
        if not graph_payload:
            return extracted
            
        nodes = graph_payload.get("nodes", [])
        for node in nodes:
            node_id = node.get("node_id")
            n_type = node.get("node_type")
            label = node.get("label", "")
            
            txt = f"Knowledge Graph Node {node_id} of type {n_type} labeled: '{label}'."
            
            ref = SourceReference(
                evidence_id=evidence_id,
                file_path=file_path,
                page_number=1,
                parser="GraphExtractor",
                parser_version="1.0.0",
                source_element=DocumentElementType.PARAGRAPH
            )
            
            extracted.append({
                "text": txt,
                "chunk_type": ChunkType.GRAPH,
                "source_reference": ref,
                "entity_ids": [],
                "timeline_event_ids": [],
                "graph_node_ids": [node_id],
                "graph_edge_ids": [],
                "correlation_cluster_ids": []
            })
        return extracted
export_graph_extractor = GraphExtractor
