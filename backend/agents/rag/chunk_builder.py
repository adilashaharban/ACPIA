# -*- coding: utf-8 -*-
"""Text chunk builder module."""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from backend.agents.rag.schema import RetrievalChunk, RetrievalSource, EmbeddingInformation, ChunkType
from backend.agents.rag.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

class ChunkBuilder:
    """Chunks text logs and links them with parent, next, and previous pointer references."""
    
    @staticmethod
    def build_chunks(
        extracted_items: List[Dict[str, Any]],
        model_name: str,
        dimension: int,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ) -> List[RetrievalChunk]:
        """Splits extracted text items into sliding-window sequence chunks.
        
        Args:
            extracted_items: Output list from extractors.
            model_name: Name of embedding model.
            dimension: Float components count.
            chunk_size: Split word count.
            chunk_overlap: Shared word overlap window.
            
        Returns:
            List of RetrievalChunk object hierarchies.
        """
        chunks: List[RetrievalChunk] = []
        embedding_info = EmbeddingInformation(
            model_name=model_name,
            model_version="1.0.0",
            embedding_dimension=dimension,
            created_at=datetime.now(timezone.utc)
        )
        
        for item in extracted_items:
            text = item.get("text", "")
            chunk_type = item.get("chunk_type", ChunkType.DOCUMENT)
            ref = item.get("source_reference")
            
            # Extract identifiers
            ent_ids = item.get("entity_ids", [])
            tl_ids = item.get("timeline_event_ids", [])
            nd_ids = item.get("graph_node_ids", [])
            ed_ids = item.get("graph_edge_ids", [])
            cl_ids = item.get("correlation_cluster_ids", [])
            
            words = text.split()
            if not words:
                continue
                
            parent_id = f"PRT-{str(uuid.uuid4())[:8]}"
            
            item_chunks = []
            idx = 0
            while idx < len(words):
                end_idx = min(idx + chunk_size, len(words))
                chunk_words = words[idx:end_idx]
                chunk_text = " ".join(chunk_words)
                
                # Advance pointer by chunk_size - chunk_overlap
                idx += max(1, chunk_size - chunk_overlap)
                
                source = RetrievalSource(
                    agent_name="rag_agent",
                    package_version="1.0.0",
                    evidence_id=ref.evidence_id,
                    case_id=None,
                    entity_ids=ent_ids,
                    timeline_event_ids=tl_ids,
                    graph_node_ids=nd_ids,
                    graph_edge_ids=ed_ids,
                    correlation_cluster_ids=cl_ids,
                    source_reference=ref
                )
                
                chunk_id = f"CHK-{str(uuid.uuid4())[:8]}"
                
                c = RetrievalChunk(
                    chunk_id=chunk_id,
                    evidence_id=ref.evidence_id,
                    chunk_type=chunk_type,
                    text=chunk_text,
                    embedding_id=f"EMB-{str(uuid.uuid4())[:8]}",
                    embedding=embedding_info,
                    token_count=len(chunk_words),
                    parent_chunk_id=parent_id,
                    source=source
                )
                item_chunks.append(c)
                if end_idx == len(words):
                    break
                
            # Interlink previous and next pointers
            for j in range(len(item_chunks)):
                if j > 0:
                    item_chunks[j].previous_chunk_id = item_chunks[j - 1].chunk_id
                if j < len(item_chunks) - 1:
                    item_chunks[j].next_chunk_id = item_chunks[j + 1].chunk_id
                    
            chunks.extend(item_chunks)
            
        return chunks
export_chunk_builder = ChunkBuilder
