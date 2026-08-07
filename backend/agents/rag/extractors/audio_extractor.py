# -*- coding: utf-8 -*-
"""Audio RAG extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.rag.schema import ChunkType

class AudioExtractor:
    """Harvests raw transcript strings from audio intelligence outputs."""
    
    @staticmethod
    def extract(audio_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        extracted = []
        if not audio_payload:
            return extracted
            
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="AudioExtractor",
            parser_version="1.0.0",
            source_element=DocumentElementType.OCR
        )
        
        transcript = audio_payload.get("transcription", {}).get("full_text", "")
        if transcript.strip():
            extracted.append({
                "text": f"Audio transcription: {transcript}",
                "chunk_type": ChunkType.AUDIO,
                "source_reference": ref,
                "entity_ids": [],
                "timeline_event_ids": [],
                "graph_node_ids": [],
                "graph_edge_ids": [],
                "correlation_cluster_ids": []
            })
        return extracted
export_audio_extractor = AudioExtractor
