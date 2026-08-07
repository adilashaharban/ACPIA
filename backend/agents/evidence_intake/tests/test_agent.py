# -*- coding: utf-8 -*-
"""Integration tests for the Evidence Intake Agent run workflow."""

from pathlib import Path
import pytest
from sqlalchemy import create_engine
from backend.database.base import Base
from backend.database.session import SessionLocal
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.evidence_intake.agent import EvidenceIntakeAgent

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch, tmp_path: Path):
    """Sets up an isolated, temporary SQLite database and storage dir for integration runs."""
    # Create in-memory SQLite URL
    db_url = f"sqlite:///{tmp_path / 'test_acpia.db'}"
    monkeypatch.setattr("backend.core.config.settings.DATABASE_URL", db_url)
    monkeypatch.setattr("backend.core.config.settings.STORAGE_DIR", tmp_path)
    
    # Reinitialize engine and database tables
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    # Patch database session generator
    from backend.database import session
    monkeypatch.setattr(session, "engine", engine)
    monkeypatch.setattr(session, "SessionLocal", session.sessionmaker(bind=engine))
    
    yield

def test_evidence_intake_agent_run_success() -> None:
    """Verifies a full successful run of the Evidence Intake Agent pipeline."""
    agent = EvidenceIntakeAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-INTEG-001",
        pipeline_stage="evidence_intake"
    )
    
    file_bytes = b"Sample text investigation evidence logs payload content."
    result = agent.run(
        context=context,
        file_bytes=file_bytes,
        filename="investigation_logs.txt",
        uploader="Special Agent Miller"
    )
    
    # Validate result contract structure
    assert result.agent == "evidence_intake"
    assert result.status == "SUCCESS"
    assert len(result.errors) == 0
    assert result.processing_context.evidence_id is not None
    
    # Validate payload details
    payload = result.payload
    assert "evidence_metadata" in payload
    meta = payload["evidence_metadata"]
    assert meta["case_id"] == "CASE-INTEG-001"
    assert meta["uploader"] == "Special Agent Miller"
    assert meta["mime_type"] == "text/plain"
    
    # Validate routing links
    assert "next_agents" in payload
    routing = payload["next_agents"]
    agents = [r["agent"] for r in routing]
    assert "metadata" in agents
    assert "document" in agents

def test_evidence_intake_agent_run_duplicate_failure() -> None:
    """Verifies that running identical file content twice results in a failure response."""
    agent = EvidenceIntakeAgent()
    
    context = ProcessingContextContract(
        case_id="CASE-INTEG-001",
        pipeline_stage="evidence_intake"
    )
    
    file_bytes = b"Unique content for duplicate test case."
    
    # First ingestion -> SUCCESS
    result_1 = agent.run(
        context=context,
        file_bytes=file_bytes,
        filename="first_doc.txt",
        uploader="Special Agent Miller"
    )
    assert result_1.status == "SUCCESS"
    
    # Second ingestion -> FAILURE
    result_2 = agent.run(
        context=context,
        file_bytes=file_bytes,
        filename="second_doc.txt",
        uploader="Special Agent Miller"
    )
    assert result_2.status == "FAILURE"
    assert len(result_2.errors) == 1
    assert "already registered" in result_2.errors[0]
