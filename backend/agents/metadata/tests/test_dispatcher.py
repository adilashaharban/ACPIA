# -*- coding: utf-8 -*-
"""Unit tests for the MetadataDispatcher."""

import pytest
from backend.agents.metadata.dispatcher import MetadataDispatcher
from backend.agents.metadata.extractors.image_extractor import ImageExtractor
from backend.agents.metadata.extractors.video_extractor import VideoExtractor
from backend.agents.metadata.extractors.generic_extractor import GenericExtractor
from backend.agents.metadata.exceptions import UnsupportedMetadataError

def test_dispatcher_select_image() -> None:
    """Verifies that an image/jpeg MIME selects ImageExtractor."""
    dispatcher = MetadataDispatcher()
    extractor = dispatcher.select_extractor("image/jpeg")
    assert extractor is ImageExtractor

def test_dispatcher_select_video() -> None:
    """Verifies that video/mp4 selects VideoExtractor."""
    dispatcher = MetadataDispatcher()
    extractor = dispatcher.select_extractor("video/mp4")
    assert extractor is VideoExtractor

def test_dispatcher_select_generic() -> None:
    """Verifies that unknown MIME types fall back to GenericExtractor."""
    dispatcher = MetadataDispatcher()
    extractor = dispatcher.select_extractor("application/octet-stream")
    assert extractor is GenericExtractor
    
    extractor2 = dispatcher.select_extractor("text/html")
    assert extractor2 is GenericExtractor

def test_dispatcher_empty_mime_error() -> None:
    """Verifies that an empty MIME string raises UnsupportedMetadataError."""
    dispatcher = MetadataDispatcher()
    with pytest.raises(UnsupportedMetadataError):
        dispatcher.select_extractor("")
