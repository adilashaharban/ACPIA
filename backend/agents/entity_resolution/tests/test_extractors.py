# -*- coding: utf-8 -*-
"""Unit tests for Entity extractors."""

from backend.agents.entity_resolution.extractors.metadata_extractor import MetadataExtractor
from backend.agents.entity_resolution.extractors.document_extractor import DocumentExtractor
from backend.agents.entity_resolution.extractors.vision_extractor import VisionExtractor
from backend.agents.entity_resolution.extractors.audio_extractor import AudioExtractor
from backend.agents.entity_resolution.schema import EntityType

def test_metadata_extractor() -> None:
    """Verifies metadata extracts file paths."""
    candidates = MetadataExtractor.extract({"file_specs": {"file_size_bytes": 1024}}, "/case/a.txt", "E1")
    assert len(candidates) == 1
    assert candidates[0].entity_type == EntityType.FILE
    assert candidates[0].raw_value == "/case/a.txt"

def test_document_extractor() -> None:
    """Verifies regex extractions."""
    payload = {
        "structure": {
            "pages": [
                {
                    "page_number": 1,
                    "text_content": "Reach me at test@domain.com or +919999988888. Also check https://acpia.org"
                }
            ]
        }
    }
    candidates = DocumentExtractor.extract(payload, "a.txt", "E1")
    # Email, Phone, URL
    types = [c.entity_type for c in candidates]
    assert EntityType.EMAIL in types
    assert EntityType.PHONE in types
    assert EntityType.URL in types

def test_vision_extractor() -> None:
    """Verifies vehicle plate harvesting."""
    payload = {
        "plates": [{"plate_id": "KA-51-1234", "confidence": 0.99}],
        "features": [{"feature_type": "clothing_color", "value": "red", "confidence": 0.95}]
    }
    candidates = VisionExtractor.extract(payload, "a.jpg", "E1")
    types = [c.entity_type for c in candidates]
    assert EntityType.PLATE in types
    assert EntityType.UNKNOWN in types

def test_audio_extractor() -> None:
    """Verifies audio keyword candidate creation."""
    payload = {
        "keywords": [{"keyword": "urgent", "confidence": 0.98}]
    }
    candidates = AudioExtractor.extract(payload, "a.wav", "E1")
    assert len(candidates) == 1
    assert candidates[0].raw_value == "urgent"
