# -*- coding: utf-8 -*-
"""Pytest fixtures for the Metadata Agent tests."""

from datetime import datetime, timezone
import os
from pathlib import Path
import pytest
from backend.agents.base import AgentResultContract, EvidencePackageContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.schemas.evidence import EvidenceMetadata
from backend.schemas.common import ProcessingState

@pytest.fixture
def test_files_dir(tmp_path: Path) -> Path:
    """Creates a temporary workspace directory for test files."""
    files_dir = tmp_path / "test_media"
    files_dir.mkdir(parents=True, exist_ok=True)
    return files_dir

@pytest.fixture
def mock_jpeg(test_files_dir: Path) -> Path:
    """Generates a dummy JPEG image file with valid dimensions."""
    img_path = test_files_dir / "valid_image.jpg"
    from PIL import Image as PILImage
    img = PILImage.new("RGB", (1, 1), color="black")
    img.save(img_path, format="JPEG")
    return img_path

@pytest.fixture
def mock_pdf(test_files_dir: Path) -> Path:
    """Generates a dummy PDF file with headers."""
    pdf_path = test_files_dir / "valid_document.pdf"
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>> endobj\n"
        b"xref\n"
        b"0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000056 00000 n \n"
        b"0000000111 00000 n \n"
        b"trailer <</Size 4 /Root 1 0 R>>\n"
        b"startxref\n"
        b"173\n"
        b"%%EOF"
    )
    pdf_path.write_bytes(pdf_bytes)
    return pdf_path

@pytest.fixture
def mock_audio(test_files_dir: Path) -> Path:
    """Generates a dummy MP3 audio file."""
    audio_path = test_files_dir / "valid_audio.mp3"
    # Minimal ID3/MP3 header
    mp3_bytes = b"ID3\x03\x00\x00\x00\x00\x00\x00\xff\xfb\x90\x44\x00\x00\x00\x00"
    audio_path.write_bytes(mp3_bytes)
    return audio_path

@pytest.fixture
def mock_video(test_files_dir: Path) -> Path:
    """Generates a dummy MP4 video file."""
    video_path = test_files_dir / "valid_video.mp4"
    # Minimal MP4 box header
    mp4_bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x08free"
    video_path.write_bytes(mp4_bytes)
    return video_path

@pytest.fixture
def mock_corrupt_file(test_files_dir: Path) -> Path:
    """Generates a corrupt file with invalid header signatures."""
    corrupt_path = test_files_dir / "corrupted.jpg"
    corrupt_path.write_bytes(b"NOT_A_JPEG_BINARY_DATA_CORRUPT")
    return corrupt_path

@pytest.fixture
def intake_result_contract(mock_jpeg: Path) -> AgentResultContract:
    """Builds a mock successful output AgentResultContract from Evidence Intake Agent."""
    import hashlib
    file_bytes = mock_jpeg.read_bytes()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    
    context = ProcessingContextContract(
        case_id="CASE-TEST-100",
        evidence_id="EVID-100",
        pipeline_stage="evidence_intake"
    )
    
    meta = EvidenceMetadata(
        evidence_id="EVID-100",
        case_id="CASE-TEST-100",
        uploader="Special Agent",
        file_path=str(mock_jpeg.resolve()),
        object_storage_path=f"s3://acpia-evidence/cases/CASE-TEST-100/valid_image.jpg",
        sha256_hash=sha256,
        mime_type="image/jpeg",
        upload_timestamp=datetime.now(timezone.utc),
        validation_status=ProcessingState.READY,
        processing_status="READY",
        routing_hints=[{"agent": "metadata", "priority": 1}],
        integrity_info={"status": "PASS"}
    )
    
    package = EvidencePackageContract(
        schema_version="1.0.0",
        agent_version="1.0.0",
        pipeline_version="1.0.0",
        evidence_metadata=meta,
        chain_of_custody_log=[{"action": "INGESTED", "performed_by": "Special Agent", "timestamp": "2026-08-06T12:00:00Z"}],
        next_agents=[{"agent": "metadata", "priority": 1}]
    )
    
    return AgentResultContract(
        agent="evidence_intake",
        status="SUCCESS",
        processing_context=context,
        payload=package.model_dump(),
        metrics={"processing_time_ms": 12.0},
        warnings=[],
        errors=[]
    )
