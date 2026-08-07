# -*- coding: utf-8 -*-
"""Metadata extractors package namespace."""

from backend.agents.metadata.extractors.generic_extractor import GenericExtractor
from backend.agents.metadata.extractors.image_extractor import ImageExtractor
from backend.agents.metadata.extractors.video_extractor import VideoExtractor
from backend.agents.metadata.extractors.audio_extractor import AudioExtractor
from backend.agents.metadata.extractors.document_extractor import DocumentExtractor

__all__ = [
    "GenericExtractor",
    "ImageExtractor",
    "VideoExtractor",
    "AudioExtractor",
    "DocumentExtractor",
]
