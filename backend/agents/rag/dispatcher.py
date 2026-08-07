# -*- coding: utf-8 -*-
"""Retrieval dispatcher."""

from typing import List, Dict, Any, Optional
from backend.agents.rag.extractors.metadata_extractor import MetadataExtractor
from backend.agents.rag.extractors.document_extractor import DocumentExtractor
from backend.agents.rag.extractors.vision_extractor import VisionExtractor
from backend.agents.rag.extractors.audio_extractor import AudioExtractor
from backend.agents.rag.extractors.entity_extractor import EntityExtractor
from backend.agents.rag.extractors.graph_extractor import GraphExtractor
from backend.agents.rag.extractors.timeline_extractor import TimelineExtractor
from backend.agents.rag.extractors.correlation_extractor import CorrelationExtractor

class Dispatcher:
    """Invokes extractors to gather text chunks parameters from upstream agent results."""
    
    @staticmethod
    def gather_text_items(
        metadata_payload: Dict[str, Any],
        document_payload: Optional[Dict[str, Any]],
        vision_payload: Optional[Dict[str, Any]],
        audio_payload: Optional[Dict[str, Any]],
        entity_payload: Optional[Dict[str, Any]],
        graph_payload: Optional[Dict[str, Any]],
        timeline_payload: Optional[Dict[str, Any]],
        correlation_payload: Optional[Dict[str, Any]],
        file_path: str,
        evidence_id: str
    ) -> List[Dict[str, Any]]:
        """Harvests raw texts from active pipeline packages.
        
        Args:
            metadata_payload: Ingestion Metadata package payload.
            document_payload: Optional Document package payload.
            vision_payload: Optional Vision package payload.
            audio_payload: Optional Audio package payload.
            entity_payload: Optional Entity Resolution package payload.
            graph_payload: Optional Knowledge Graph package payload.
            timeline_payload: Optional Timeline package payload.
            correlation_payload: Optional Correlation package payload.
            file_path: Evidence file path.
            evidence_id: Ingestion evidence ID.
            
        Returns:
            Aggregated dictionary items.
        """
        extracted = []
        
        extracted.extend(MetadataExtractor.extract(metadata_payload, file_path, evidence_id))
        
        if document_payload:
            extracted.extend(DocumentExtractor.extract(document_payload, file_path, evidence_id))
        if vision_payload:
            extracted.extend(VisionExtractor.extract(vision_payload, file_path, evidence_id))
        if audio_payload:
            extracted.extend(AudioExtractor.extract(audio_payload, file_path, evidence_id))
        if entity_payload:
            extracted.extend(EntityExtractor.extract(entity_payload, file_path, evidence_id))
        if graph_payload:
            extracted.extend(GraphExtractor.extract(graph_payload, file_path, evidence_id))
        if timeline_payload:
            extracted.extend(TimelineExtractor.extract(timeline_payload, file_path, evidence_id))
        if correlation_payload:
            extracted.extend(CorrelationExtractor.extract(correlation_payload, file_path, evidence_id))
            
        return extracted
export_dispatcher = Dispatcher
