# -*- coding: utf-8 -*-
"""Timeline extraction dispatcher."""

from typing import List, Dict, Any, Optional
from backend.agents.cross_evidence_correlation.extractors.metadata_extractor import MetadataExtractor
from backend.agents.cross_evidence_correlation.extractors.document_extractor import DocumentExtractor
from backend.agents.cross_evidence_correlation.extractors.vision_extractor import VisionExtractor
from backend.agents.cross_evidence_correlation.extractors.audio_extractor import AudioExtractor
from backend.agents.cross_evidence_correlation.extractors.entity_extractor import EntityExtractor
from backend.agents.cross_evidence_correlation.extractors.graph_extractor import GraphExtractor
from backend.agents.cross_evidence_correlation.extractors.timeline_extractor import TimelineExtractor
from backend.agents.cross_evidence_correlation.schema import CandidateObservation

class Dispatcher:
    """Invokes modal extractors to gather candidate observations."""
    
    @staticmethod
    def gather_observations(
        metadata_payload: Dict[str, Any],
        document_payload: Optional[Dict[str, Any]],
        vision_payload: Optional[Dict[str, Any]],
        audio_payload: Optional[Dict[str, Any]],
        entity_payload: Optional[Dict[str, Any]],
        graph_payload: Optional[Dict[str, Any]],
        timeline_payload: Optional[Dict[str, Any]],
        file_path: str,
        evidence_id: str
    ) -> List[CandidateObservation]:
        """Harvests candidates from active pipeline packages.
        
        Args:
            metadata_payload: Ingestion Metadata package payload.
            document_payload: Optional Document package payload.
            vision_payload: Optional Vision package payload.
            audio_payload: Optional Audio package payload.
            entity_payload: Optional Entity Resolution package payload.
            graph_payload: Optional Knowledge Graph package payload.
            timeline_payload: Optional Timeline package payload.
            file_path: Evidence file path.
            evidence_id: Ingestion evidence ID.
            
        Returns:
            Aggregated CandidateObservation list.
        """
        candidates: List[CandidateObservation] = []
        
        candidates.extend(MetadataExtractor.extract(metadata_payload, file_path, evidence_id))
        
        if document_payload:
            candidates.extend(DocumentExtractor.extract(document_payload, file_path, evidence_id))
        if vision_payload:
            candidates.extend(VisionExtractor.extract(vision_payload, file_path, evidence_id))
        if audio_payload:
            candidates.extend(AudioExtractor.extract(audio_payload, file_path, evidence_id))
        if entity_payload:
            candidates.extend(EntityExtractor.extract(entity_payload, file_path, evidence_id))
        if graph_payload:
            candidates.extend(GraphExtractor.extract(graph_payload, file_path, evidence_id))
        if timeline_payload:
            candidates.extend(TimelineExtractor.extract(timeline_payload, file_path, evidence_id))
            
        return candidates
export_dispatcher = Dispatcher
