# -*- coding: utf-8 -*-
"""Pytest fixtures for Entity Resolution Agent."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import pytest
from backend.database.base import Base
from backend.agents.base import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract

@pytest.fixture(autouse=True)
def setup_db_context(monkeypatch, tmp_path: Path):
    """Mocks database connection."""
    db_url = f"sqlite:///{tmp_path / 'test_ent_acpia.db'}"
    monkeypatch.setattr("backend.core.config.settings.DATABASE_URL", db_url)
    monkeypatch.setattr("backend.core.config.settings.STORAGE_DIR", tmp_path)
    
    from sqlalchemy import create_engine
    engine = create_engine(db_url)
    
    # Import models to register them on Base.metadata
    from backend.database.models.evidence import Evidence
    from backend.database.models.chain_of_custody import ChainOfCustody
    
    Base.metadata.create_all(engine)
    
    from backend.database import session
    monkeypatch.setattr(session, "engine", engine)
    monkeypatch.setattr(session, "SessionLocal", session.sessionmaker(bind=engine))
    yield

@pytest.fixture
def mock_evidence_file(tmp_path: Path) -> Path:
    """Creates mock evidence file."""
    p = tmp_path / "case_file.txt"
    p.write_text("Hello. Contact me at john.doe@mail.com or +91 99999 88888.")
    return p

@pytest.fixture
def metadata_result_contract(mock_evidence_file: Path) -> AgentResultContract:
    """Mock Metadata output."""
    file_bytes = mock_evidence_file.read_bytes()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    evidence_id = "EVID-ENT-1"
    case_id = "CASE-ENT-1"
    
    from backend.database.session import SessionLocal
    from backend.database.models.evidence import Evidence
    db = SessionLocal()
    try:
        db_ev = Evidence(
            evidence_id=evidence_id,
            case_id=case_id,
            uploader="Officer",
            file_path=str(mock_evidence_file.resolve()),
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
    
    payload = {
        "evidence_id": evidence_id,
        "file_specs": {"file_size_bytes": len(file_bytes)}
    }
    
    return AgentResultContract(
        agent="metadata_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={},
        warnings=[],
        errors=[]
    )

@pytest.fixture
def document_result_contract() -> AgentResultContract:
    """Mock Document Intelligence output."""
    context = ProcessingContextContract(case_id="C1", evidence_id="EVID-ENT-1", pipeline_stage="document_intelligence")
    payload = {
        "structure": {
            "pages": [
                {
                    "page_number": 1,
                    "text_content": "John Doe has email john.doe@mail.com and phone +91 99999 88888. Web is http://example.com"
                }
            ]
        }
    }
    return AgentResultContract(
        agent="document_intelligence_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={},
        warnings=[],
        errors=[]
    )

@pytest.fixture
def vision_result_contract() -> AgentResultContract:
    """Mock Vision Intelligence output."""
    context = ProcessingContextContract(case_id="C1", evidence_id="EVID-ENT-1", pipeline_stage="vision_intelligence")
    payload = {
        "plates": [{"plate_id": "KA-51-MM-1234", "confidence": 0.96}],
        "features": [{"feature_type": "clothing_color", "value": "blue", "confidence": 0.95}]
    }
    return AgentResultContract(
        agent="vision_intelligence_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={},
        warnings=[],
        errors=[]
    )

@pytest.fixture
def audio_result_contract() -> AgentResultContract:
    """Mock Audio Intelligence output."""
    context = ProcessingContextContract(case_id="C1", evidence_id="EVID-ENT-1", pipeline_stage="audio_intelligence")
    payload = {
        "keywords": [{"keyword": "urgent", "confidence": 0.99}]
    }
    return AgentResultContract(
        agent="audio_intelligence_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={},
        warnings=[],
        errors=[]
    )
