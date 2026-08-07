# -*- coding: utf-8 -*-
"""Pytest fixtures for Vision Intelligence Agent."""

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import pytest
from PIL import Image
from backend.database.base import Base
from backend.database.session import SessionLocal
from backend.database.models.evidence import Evidence
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract

@pytest.fixture(autouse=True)
def setup_db_context(monkeypatch, tmp_path: Path):
    """Mocks backend database tables and updates configuration variables for isolated runs."""
    db_url = f"sqlite:///{tmp_path / 'test_vis_acpia.db'}"
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
    """Fixture providing a temporary target directory for image media."""
    d = tmp_path / "vision_media"
    d.mkdir(parents=True, exist_ok=True)
    return d

@pytest.fixture
def mock_image(test_files_dir: Path) -> Path:
    """Creates a real valid minimal 100x100 RGB JPEG image file."""
    p = test_files_dir / "valid_image.jpg"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(p, format="JPEG")
    return p

@pytest.fixture
def mock_corrupt_image(test_files_dir: Path) -> Path:
    """Creates a corrupt image file containing arbitrary byte blocks."""
    p = test_files_dir / "corrupted.jpg"
    p.write_bytes(b"invalid jpeg graphics bytes block")
    return p

@pytest.fixture
def metadata_result_contract(mock_image: Path) -> AgentResultContract:
    """Creates a mock input Metadata Agent result contract."""
    file_bytes = mock_image.read_bytes()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    evidence_id = "EVID-VIS-99"
    case_id = "CASE-VIS-99"
    
    # Pre-register evidence in DB so pipeline can query it
    from backend.database.session import SessionLocal
    db = SessionLocal()
    try:
        db_ev = Evidence(
            evidence_id=evidence_id,
            case_id=case_id,
            uploader="Officer",
            file_path=str(mock_image.resolve()),
            object_storage_path=f"s3://acpia/cases/{case_id}/{evidence_id}",
            sha256_hash=sha256,
            mime_type="image/jpeg",
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
    
    payload = {
        "evidence_id": evidence_id,
        "summary": {"file_type_category": "image", "has_gps": False, "is_media": True},
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
        metrics={"processing_time_ms": 20.0},
        warnings=[],
        errors=[]
    )
