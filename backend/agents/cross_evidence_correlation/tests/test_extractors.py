# -*- coding: utf-8 -*-
"""Unit tests for Cross-Evidence Correlation extractors."""

from backend.agents.cross_evidence_correlation.extractors.metadata_extractor import MetadataExtractor
from backend.agents.cross_evidence_correlation.extractors.document_extractor import DocumentExtractor
from backend.agents.cross_evidence_correlation.extractors.vision_extractor import VisionExtractor
from backend.agents.cross_evidence_correlation.extractors.audio_extractor import AudioExtractor
from backend.agents.cross_evidence_correlation.extractors.entity_extractor import EntityExtractor
from backend.agents.cross_evidence_correlation.extractors.graph_extractor import GraphExtractor
from backend.agents.cross_evidence_correlation.extractors.timeline_extractor import TimelineExtractor
from backend.agents.cross_evidence_correlation.schema import CorrelationType

def test_metadata_extractor() -> None:
    """Verifies metadata extracts file creation."""
    payload = {"file_specs": {"creation_time": "2026-08-01T10:00:00Z"}}
    candidates = MetadataExtractor.extract(payload, "a.txt", "E1")
    assert len(candidates) == 1
    assert candidates[0].observation_type == CorrelationType.TEMPORAL_MATCH
    assert candidates[0].raw_value == "2026-08-01T10:00:00Z"

def test_document_extractor() -> None:
    """Verifies regex datetime text extracts."""
    payload = {
        "structure": {
            "pages": [
                {
                    "page_number": 1,
                    "text_content": "Observed timestamp inside page content: 2026-08-01 10:15:00"
                }
            ]
        }
    }
    candidates = DocumentExtractor.extract(payload, "a.txt", "E1")
    assert len(candidates) == 1
    assert candidates[0].raw_value == "2026-08-01 10:15:00"

def test_vision_extractor() -> None:
    """Verifies EXIF date extraction."""
    payload = {"exif": {"DateTimeOriginal": "2026-08-01T10:20:00Z"}}
    candidates = VisionExtractor.extract(payload, "a.jpg", "E1")
    assert len(candidates) == 1
    assert candidates[0].observation_type == CorrelationType.TEMPORAL_MATCH

def test_audio_extractor() -> None:
    """Verifies audio recording date extraction."""
    payload = {"media_info": {"creation_time": "2026-08-01T10:25:00Z"}}
    candidates = AudioExtractor.extract(payload, "a.wav", "E1")
    assert len(candidates) == 1
    assert candidates[0].observation_type == CorrelationType.TEMPORAL_MATCH

def test_entity_extractor() -> None:
    """Verifies resolved entity extraction."""
    payload = {
        "entities": [
            {
                "entity_id": "ENT-1",
                "entity_type": "PERSON",
                "canonical_name": "John Doe",
                "confidence_breakdown": {"final_confidence": 0.95}
            }
        ]
    }
    candidates = EntityExtractor.extract(payload, "a.txt", "E1")
    assert len(candidates) == 1
    assert candidates[0].observation_type == CorrelationType.ENTITY_MATCH
    assert candidates[0].raw_value == "John Doe"

def test_graph_extractor() -> None:
    """Verifies graph event and location property harvesting."""
    payload = {
        "nodes": [
            {
                "node_id": "ND-LOC-1",
                "node_type": "LOCATION",
                "label": "Location",
                "properties": [
                    {
                        "key": "occurred_at",
                        "value": "2026-08-01T10:05:00Z",
                        "confidence": 0.95
                    }
                ]
            }
        ]
    }
    candidates = GraphExtractor.extract(payload, "a.txt", "E1")
    assert len(candidates) == 1
    assert candidates[0].raw_value == "2026-08-01T10:05:00Z"

def test_timeline_extractor() -> None:
    """Verifies timeline package events extraction."""
    payload = {
        "events": [
            {
                "event_id": "EVT-1",
                "event_type": "FILE_CREATED",
                "title": "Created",
                "original_timestamp": "2026-08-01T10:00:00Z",
                "normalized_timestamp_utc": "2026-08-01T10:00:00Z",
                "confidence": 1.0
            }
        ]
    }
    candidates = TimelineExtractor.extract(payload, "a.txt", "E1")
    assert len(candidates) == 1
    assert candidates[0].raw_value == "2026-08-01T10:00:00Z"
