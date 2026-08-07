# -*- coding: utf-8 -*-
"""Unit tests for RAG extractors."""

from backend.agents.rag.extractors.metadata_extractor import MetadataExtractor
from backend.agents.rag.extractors.document_extractor import DocumentExtractor
from backend.agents.rag.extractors.vision_extractor import VisionExtractor
from backend.agents.rag.extractors.audio_extractor import AudioExtractor
from backend.agents.rag.extractors.entity_extractor import EntityExtractor
from backend.agents.rag.extractors.graph_extractor import GraphExtractor
from backend.agents.rag.extractors.timeline_extractor import TimelineExtractor
from backend.agents.rag.extractors.correlation_extractor import CorrelationExtractor
from backend.agents.rag.schema import ChunkType

def test_extractors() -> None:
    """Verifies that all modal extractors retrieve valid text descriptions."""
    items = MetadataExtractor.extract({"file_specs": {"creation_time": "2026-08-01"}}, "a.txt", "E1")
    assert len(items) == 1
    assert items[0]["chunk_type"] == ChunkType.DOCUMENT
    
    docs = DocumentExtractor.extract({"structure": {"pages": [{"text_content": "Page content"}]}}, "a.txt", "E1")
    assert len(docs) == 1
    
    vis = VisionExtractor.extract({"exif": {"DateTimeOriginal": "2026-08-01"}, "objects": [{"label": "Person"}]}, "a.jpg", "E1")
    assert len(vis) == 1
    
    aud = AudioExtractor.extract({"transcription": {"full_text": "Acoustic words text"}}, "a.wav", "E1")
    assert len(aud) == 1
    
    ent = EntityExtractor.extract({"entities": [{"entity_id": "ENT-1", "canonical_name": "John", "entity_type": "PERSON"}]}, "a.txt", "E1")
    assert len(ent) == 1
    assert ent[0]["chunk_type"] == ChunkType.ENTITY
    
    grp = GraphExtractor.extract({"nodes": [{"node_id": "ND-1", "node_type": "LOCATION", "label": "Node Address"}]}, "a.txt", "E1")
    assert len(grp) == 1
    
    tline = TimelineExtractor.extract({"events": [{"event_id": "EVT-1", "title": "Creation event", "normalized_timestamp_utc": "2026-08-01"}]}, "a.txt", "E1")
    assert len(tline) == 1
    
    corr = CorrelationExtractor.extract({"clusters": [{"cluster_id": "CL-1", "cluster_name": "Cluster A"}]}, "a.txt", "E1")
    assert len(corr) == 1
