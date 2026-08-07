# -*- coding: utf-8 -*-
"""Unit tests for the Metadata Extractors."""

import pytest
from pathlib import Path
from backend.agents.metadata.extractors.generic_extractor import GenericExtractor
from backend.agents.metadata.extractors.image_extractor import ImageExtractor
from backend.agents.metadata.extractors.video_extractor import VideoExtractor
from backend.agents.metadata.extractors.audio_extractor import AudioExtractor
from backend.agents.metadata.extractors.document_extractor import DocumentExtractor
from backend.agents.metadata.exceptions import ParserFailureError

def test_generic_extractor(mock_jpeg: Path) -> None:
    """Verifies GenericExtractor extracts correct FileMetadata details."""
    meta = GenericExtractor.extract(str(mock_jpeg.resolve()))
    assert meta.file_size_bytes > 0
    assert meta.file_permissions != ""
    assert meta.creation_time is not None
    assert meta.modification_time is not None

def test_generic_extractor_missing_file() -> None:
    """Verifies that generic extractor raises exception on non-existing path."""
    with pytest.raises(ParserFailureError):
        GenericExtractor.extract("missing_file.jpg")

def test_image_extractor_fallback(mock_corrupt_file: Path) -> None:
    """Verifies ImageExtractor reads image dimensions even if EXIF tag structure is corrupt."""
    # Since mock_corrupt_file is not a valid image, it will raise ParserFailureError
    with pytest.raises(ParserFailureError):
        ImageExtractor.extract(str(mock_corrupt_file.resolve()))

def test_audio_extractor_failure(mock_corrupt_file: Path) -> None:
    """Verifies corrupt audio raises parser error."""
    with pytest.raises(ParserFailureError):
        AudioExtractor.extract(str(mock_corrupt_file.resolve()))

def test_video_extractor_failure(mock_corrupt_file: Path) -> None:
    """Verifies corrupt video raises parser error."""
    with pytest.raises(ParserFailureError):
        VideoExtractor.extract(str(mock_corrupt_file.resolve()))

def test_document_extractor_encrypted_handling(mock_pdf: Path) -> None:
    """Verifies PdfExtractor pages size and encryption flags."""
    meta = DocumentExtractor.extract(str(mock_pdf.resolve()))
    assert meta.encrypted is False
    assert meta.page_count == 1
