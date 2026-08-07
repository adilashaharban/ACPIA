# -*- coding: utf-8 -*-
"""Entity RAG extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.rag.schema import ChunkType

class EntityExtractor:
    """Harvests canonical resolved entity lists from entity resolution outputs."""
    
    @staticmethod
    def extract(entity_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        extracted = []
        if not entity_payload:
            return extracted
            
        entities = entity_payload.get("entities", [])
        for ent in entities:
            ent_id = ent.get("entity_id")
            name = ent.get("canonical_name")
            e_type = ent.get("entity_type")
            
            # Form citation
            txt = f"Resolved canonical entity {ent_id} of type {e_type} named: '{name}'."
            
            refs = ent.get("source_references", [])
            if refs:
                ref = SourceReference.model_validate(refs[0])
            else:
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=1,
                    parser="EntityExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                
            extracted.append({
                "text": txt,
                "chunk_type": ChunkType.ENTITY,
                "source_reference": ref,
                "entity_ids": [ent_id],
                "timeline_event_ids": [],
                "graph_node_ids": [],
                "graph_edge_ids": [],
                "correlation_cluster_ids": []
            })
        return extracted
export_entity_extractor = EntityExtractor
