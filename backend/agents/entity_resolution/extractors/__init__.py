# -*- coding: utf-8 -*-
"""Extractors package namespace."""

from backend.agents.entity_resolution.extractors.metadata_extractor import MetadataExtractor
from backend.agents.entity_resolution.extractors.document_extractor import DocumentExtractor
from backend.agents.entity_resolution.extractors.vision_extractor import VisionExtractor
from backend.agents.entity_resolution.extractors.audio_extractor import AudioExtractor

__all__ = [
    "MetadataExtractor",
    "DocumentExtractor",
    "VisionExtractor",
    "AudioExtractor",
]
