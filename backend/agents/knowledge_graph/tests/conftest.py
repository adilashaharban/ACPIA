# -*- coding: utf-8 -*-
"""Pytest fixtures for Knowledge Graph Agent."""

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
    db_url = f"sqlite:///{tmp_path / 'test_kg_acpia.db'}"
    monkeypatch.setattr("backend.core.config.settings.DATABASE_URL", db_url)
    monkeypatch.setattr("backend.core.config.settings.STORAGE_DIR", tmp_path)
    
    from sqlalchemy import create_engine
    engine = create_engine(db_url)
    
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
    p.write_text("Case details content.")
    return p

@pytest.fixture
def metadata_result_contract(mock_evidence_file: Path) -> AgentResultContract:
    """Mock Metadata output."""
    file_bytes = mock_evidence_file.read_bytes()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    evidence_id = "EVID-KG-1"
    case_id = "CASE-KG-1"
    
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
def entity_resolution_result_contract() -> AgentResultContract:
    """Mock Entity Resolution Agent output payload."""
    context = ProcessingContextContract(case_id="CASE-KG-1", evidence_id="EVID-KG-1", pipeline_stage="entity_resolution")
    
    # We build a valid EntityResolutionPackage payload containing a PERSON and a PHONE
    payload = {
        "schema_version": "1.0.0",
        "entities": [
            {
                "entity_id": "ENT-PER-john1234",
                "entity_type": "PERSON",
                "canonical_name": "John Doe",
                "aliases": [],
                "attributes": [
                    {
                        "key": "name",
                        "value": "John Doe",
                        "confidence": 0.95,
                        "source_reference": {
                            "evidence_id": "EVID-KG-1",
                            "file_path": "mock.txt",
                            "page_number": 1,
                            "parser": "test",
                            "parser_version": "1.0.0",
                            "source_element": "OCR"
                        }
                    }
                ],
                "confidence_breakdown": {
                    "exact_match_score": 1.0,
                    "fuzzy_match_score": 0.0,
                    "cross_modal_score": 0.0,
                    "evidence_count_score": 0.5,
                    "final_confidence": 0.95
                },
                "source_references": [
                    {
                        "evidence_id": "EVID-KG-1",
                        "file_path": "mock.txt",
                        "page_number": 1,
                        "parser": "test",
                        "parser_version": "1.0.0",
                        "source_element": "OCR"
                    }
                ],
                "supporting_observations": [
                    {
                        "observation_id": "obs1",
                        "evidence_id": "EVID-KG-1",
                        "entity_type": "PERSON",
                        "raw_value": "John Doe",
                        "normalized_value": "john doe",
                        "confidence": 0.95,
                        "source_reference": {
                            "evidence_id": "EVID-KG-1",
                            "file_path": "mock.txt",
                            "page_number": 1,
                            "parser": "test",
                            "parser_version": "1.0.0",
                            "source_element": "OCR"
                        }
                    }
                ],
                "linked_evidence": ["EVID-KG-1"],
                "creation_method": "EXACT_MATCH"
            },
            {
                "entity_id": "ENT-PHO-phone777",
                "entity_type": "PHONE",
                "canonical_name": "+919999988888",
                "aliases": [],
                "attributes": [],
                "confidence_breakdown": {
                    "exact_match_score": 1.0,
                    "fuzzy_match_score": 0.0,
                    "cross_modal_score": 0.0,
                    "evidence_count_score": 0.5,
                    "final_confidence": 0.90
                },
                "source_references": [
                    {
                        "evidence_id": "EVID-KG-1",
                        "file_path": "mock.txt",
                        "page_number": 1,
                        "parser": "test",
                        "parser_version": "1.0.0",
                        "source_element": "OCR"
                    }
                ],
                "supporting_observations": [
                    {
                        "observation_id": "obs2",
                        "evidence_id": "EVID-KG-1",
                        "entity_type": "PHONE",
                        "raw_value": "+91 99999 88888",
                        "normalized_value": "+919999988888",
                        "confidence": 0.90,
                        "source_reference": {
                            "evidence_id": "EVID-KG-1",
                            "file_path": "mock.txt",
                            "page_number": 1,
                            "parser": "test",
                            "parser_version": "1.0.0",
                            "source_element": "OCR"
                        }
                    }
                ],
                "linked_evidence": ["EVID-KG-1"],
                "creation_method": "EXACT_MATCH"
            }
        ],
        "statistics": {"total_candidates": 2, "resolved_count": 2, "merged_count": 0, "cluster_count": 2},
        "validation": {"integrity_status": "PASS"},
        "metrics": {"processing_time_ms": 10.0, "candidate_count": 2, "normalization_count": 2, "match_count": 0, "merge_count": 0},
        "summary": {"resolved_types": {"PERSON": 1, "PHONE": 1}, "average_resolution_confidence": 0.925}
    }
    
    return AgentResultContract(
        agent="entity_resolution_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={},
        warnings=[],
        errors=[]
    )
