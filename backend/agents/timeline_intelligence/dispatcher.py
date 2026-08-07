# -*- coding: utf-8 -*-
"""Timeline extraction dispatcher."""

from typing import List, Dict, Any, Optional
from backend.agents.timeline_intelligence.extractors.metadata_extractor import MetadataExtractor
from backend.agents.timeline_intelligence.extractors.document_extractor import DocumentExtractor
from backend.agents.timeline_intelligence.extractors.vision_extractor import VisionExtractor
from backend.agents.timeline_intelligence.extractors.audio_extractor import AudioExtractor
from backend.agents.timeline_intelligence.extractors.graph_extractor import GraphExtractor

class TimelineDispatcher:
    """Invokes extractors to compile candidate temporal observations."""
    
    @staticmethod
    def gather_candidates(
        metadata_payload: Dict[str, Any],
        document_payload: Optional[Dict[str, Any]],
        vision_payload: Optional[Dict[str, Any]],
        audio_payload: Optional[Dict[str, Any]],
        graph_payload: Optional[Dict[str, Any]],
        file_path: str,
        evidence_id: str
    ) -> List[Dict[str, Any]]:
        """Invokes appropriate extractors based on available payloads.
        
        Args:
            metadata_payload: Metadata package dictionary.
            document_payload: Document package dictionary.
            vision_payload: Vision package dictionary.
            audio_payload: Audio package dictionary.
            graph_payload: Knowledge Graph package dictionary.
            file_path: Target evidence file path.
            evidence_id: Ingestion evidence ID.
            
        Returns:
            Aggregated list of raw candidate dictionaries.
        """
        candidates: List[Dict[str, Any]] = []
        
        # Metadata extractor runs on happy path
        candidates.extend(MetadataExtractor.extract(metadata_payload, file_path, evidence_id))
        
        # Optional dispatchings
        if document_payload:
            candidates.extend(DocumentExtractor.extract(document_payload, file_path, evidence_id))
        if vision_payload:
            candidates.extend(VisionExtractor.extract(vision_payload, file_path, evidence_id))
        if audio_payload:
            candidates.extend(AudioExtractor.extract(audio_payload, file_path, evidence_id))
        if graph_payload:
            candidates.extend(GraphExtractor.extract(graph_payload, file_path, evidence_id))
            
        return candidates
export_dispatcher = TimelineDispatcher
