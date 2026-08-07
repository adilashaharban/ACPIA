# -*- coding: utf-8 -*-
"""Unit tests for registry module."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.base import Base
from backend.agents.evidence_intake.registry import EvidenceRegistry
from backend.agents.evidence_intake.exceptions import DuplicateEvidenceError

@pytest.fixture
def db_session():
    """Provides an in-memory SQLite session for isolated database tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_registry_register_and_custody(db_session) -> None:
    """Verifies that evidence is registered and custody logs are logged."""
    registry = EvidenceRegistry(db_session)
    
    sha256 = "d3b07384d113edec49eaa6238ad5ff00b71947b19cf8a1e2852b49b6b90757d5"
    case_id = "CASE-101"
    
    # Register file
    evidence = registry.register_evidence(
        case_id=case_id,
        uploader="Agent Smith",
        file_path="/tmp/fake.png",
        object_storage_path="s3://evidence/fake.png",
        sha256_hash=sha256,
        mime_type="image/png"
    )
    
    assert evidence.evidence_id is not None
    assert evidence.case_id == case_id
    assert evidence.sha256_hash == sha256
    
    # Assert Chain of Custody created
    trail = registry.get_custody_trail(evidence.evidence_id)
    assert len(trail) == 1
    assert trail[0].action == "INGESTED"
    assert trail[0].performed_by == "Agent Smith"

def test_registry_duplicate_check(db_session) -> None:
    """Verifies that duplicate registration raises DuplicateEvidenceError."""
    registry = EvidenceRegistry(db_session)
    sha256 = "d3b07384d113edec49eaa6238ad5ff00b71947b19cf8a1e2852b49b6b90757d5"
    
    registry.register_evidence(
        case_id="CASE-101",
        uploader="Agent Smith",
        file_path="/tmp/fake.png",
        object_storage_path="s3://evidence/fake.png",
        sha256_hash=sha256,
        mime_type="image/png"
    )
    
    # Registering duplicate hash raises error
    with pytest.raises(DuplicateEvidenceError):
        registry.register_evidence(
            case_id="CASE-102",
            uploader="Agent Jones",
            file_path="/tmp/fake2.png",
            object_storage_path="s3://evidence/fake2.png",
            sha256_hash=sha256,
            mime_type="image/png"
        )
