# -*- coding: utf-8 -*-
"""Pytest fixtures for Document Intelligence Agent."""

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import pytest
from backend.database.base import Base
from backend.database.session import SessionLocal
from backend.database.models.evidence import Evidence
from backend.database.repositories.evidence_repository import EvidenceRepository
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.schemas.evidence import EvidenceMetadata
from backend.schemas.common import ProcessingState

@pytest.fixture(autouse=True)
def setup_db_context(monkeypatch, tmp_path: Path):
    """Mocks backend database tables and updates configuration variables for isolated runs."""
    db_url = f"sqlite:///{tmp_path / 'test_doc_acpia.db'}"
    monkeypatch.setattr("backend.core.config.settings.DATABASE_URL", db_url)
    monkeypatch.setattr("backend.core.config.settings.STORAGE_DIR", tmp_path)
    
    from sqlalchemy import create_engine
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    from backend.database import session
    monkeypatch.setattr(session, "engine", engine)
    monkeypatch.setattr(session, "SessionLocal", session.sessionmaker(bind=engine))
    yield

@pytest.fixture
def test_files_dir(tmp_path: Path) -> Path:
    """Fixture providing a temporary target directory for files."""
    d = tmp_path / "doc_media"
    d.mkdir(parents=True, exist_ok=True)
    return d

@pytest.fixture
def mock_txt(test_files_dir: Path) -> Path:
    """Creates a mock clean text file."""
    p = test_files_dir / "evidence.txt"
    p.write_text("Line 1 text content.\n\nLine 2 text content block.", encoding="utf-8")
    return p

@pytest.fixture
def mock_csv(test_files_dir: Path) -> Path:
    """Creates a mock CSV file."""
    p = test_files_dir / "data.csv"
    p.write_text("ID,Name,Role\n1,Suspect,Owner\n2,Witness,Contact", encoding="utf-8")
    return p

@pytest.fixture
def mock_json(test_files_dir: Path) -> Path:
    """Creates a mock JSON file."""
    p = test_files_dir / "export.json"
    p.write_text('{"case_id": "CASE-9", "suspect": {"name": "Anonymous"}}', encoding="utf-8")
    return p

@pytest.fixture
def mock_xml(test_files_dir: Path) -> Path:
    """Creates a mock XML file."""
    p = test_files_dir / "logs.xml"
    p.write_text("<root><entry id='1'>Message text log.</entry></root>", encoding="utf-8")
    return p

@pytest.fixture
def mock_html(test_files_dir: Path) -> Path:
    """Creates a mock HTML file."""
    p = test_files_dir / "chat.html"
    p.write_text("<html><body><h1>Header Title</h1><p>Body message paragraph.</p></body></html>", encoding="utf-8")
    return p

@pytest.fixture
def mock_whatsapp(test_files_dir: Path) -> Path:
    """Creates a mock WhatsApp text export log."""
    p = test_files_dir / "whatsapp_chat.txt"
    p.write_text("18/07/2026, 14:32 - Officer: Suspect message.\n[18/07/2026, 14:35:00] Suspect: Understood.", encoding="utf-8")
    return p

@pytest.fixture
def mock_eml(test_files_dir: Path) -> Path:
    """Creates a mock EML email file."""
    p = test_files_dir / "email.eml"
    p.write_text("From: sender@domain.com\nTo: dest@domain.com\nSubject: Case files\n\nEmail body text content block.", encoding="utf-8")
    return p

@pytest.fixture
def mock_pdf(test_files_dir: Path) -> Path:
    """Creates a mock minimal PDF file (scanned PDF representation)."""
    p = test_files_dir / "scanned_doc.pdf"
    # Write a simple text file, dispatcher will select PDF parser but it will yield no text
    # triggering OCR. (pdfplumber cannot parse standard text files as PDFs and throws error,
    # so we mock a minimal PDF file with text).
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
    p.write_bytes(pdf_bytes)
    return p

@pytest.fixture
def metadata_result_contract(mock_txt: Path) -> AgentResultContract:
    """Creates a mock input Metadata Agent result contract."""
    file_bytes = mock_txt.read_bytes()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    evidence_id = "EVID-DOC-100"
    case_id = "CASE-DOC-100"
    
    # Pre-register evidence in DB so pipeline can query it
    from backend.database.session import SessionLocal
    db = SessionLocal()
    try:
        db_ev = Evidence(
            evidence_id=evidence_id,
            case_id=case_id,
            uploader="Officer",
            file_path=str(mock_txt.resolve()),
            object_storage_path=f"s3://acpia/cases/{case_id}/{evidence_id}",
            sha256_hash=sha256,
            mime_type="text/plain",
            upload_timestamp=datetime.now(timezone.utc),
            validation_status="READY",
            processing_status="READY",
            routing_hints=[],
            integrity_info={}
        )
        db.add(db_ev)
        db.commit()
    finally:
        db.close()
        
    context = ProcessingContextContract(
        case_id=case_id,
        evidence_id=evidence_id,
        pipeline_stage="metadata"
    )
    
    # Metadata Agent payload representation
    payload = {
        "evidence_id": evidence_id,
        "summary": {"file_type_category": "text", "has_gps": False, "is_media": False},
        "file_specs": {
            "file_size_bytes": len(file_bytes),
            "file_permissions": "-rw-r--r--",
            "creation_time": datetime.now(timezone.utc).isoformat(),
            "modification_time": datetime.now(timezone.utc).isoformat()
        },
        "validation": {"integrity_verification": "PASS"}
    }
    
    return AgentResultContract(
        agent="metadata_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={"processing_time_ms": 15.0},
        warnings=[],
        errors=[]
    )
