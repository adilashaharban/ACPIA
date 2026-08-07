# -*- coding: utf-8 -*-
"""Pytest fixtures for RAG Agent."""

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
    db_url = f"sqlite:///{tmp_path / 'test_rag_acpia.db'}"
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
    evidence_id = "EVID-RAG-1"
    case_id = "CASE-RAG-1"
    
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
        "file_specs": {
            "file_size_bytes": len(file_bytes),
            "creation_time": "2026-08-01T10:00:00Z",
            "modification_time": "2026-08-01T10:30:00Z"
        }
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
    context = ProcessingContextContract(case_id="CASE-RAG-1", evidence_id="EVID-RAG-1", pipeline_stage="document_intelligence")
    payload = {
        "structure": {
            "pages": [
                {
                    "page_number": 1,
                    "text_content": "Observed timestamp inside page content: 2026-08-01 10:15:00"
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
    context = ProcessingContextContract(case_id="CASE-RAG-1", evidence_id="EVID-RAG-1", pipeline_stage="vision_intelligence")
    payload = {
        "exif": {"DateTimeOriginal": "2026-08-01T10:20:00Z"}
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
    context = ProcessingContextContract(case_id="CASE-RAG-1", evidence_id="EVID-RAG-1", pipeline_stage="audio_intelligence")
    payload = {
        "media_info": {"creation_time": "2026-08-01T10:25:00Z"}
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

@pytest.fixture
def entity_result_contract() -> AgentResultContract:
    """Mock Entity Resolution output."""
    context = ProcessingContextContract(case_id="CASE-RAG-1", evidence_id="EVID-RAG-1", pipeline_stage="entity_resolution")
    payload = {
        "entities": [
            {
                "entity_id": "ENT-PER-john123",
                "entity_type": "PERSON",
                "canonical_name": "John Doe",
                "confidence_breakdown": {"final_confidence": 0.95},
                "source_references": [
                    {
                        "evidence_id": "EVID-RAG-1",
                        "file_path": "mock.txt",
                        "page_number": 1,
                        "parser": "test",
                        "parser_version": "1.0.0",
                        "source_element": "OCR"
                    }
                ]
            }
        ]
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

@pytest.fixture
def graph_result_contract() -> AgentResultContract:
    """Mock Knowledge Graph Agent output."""
    context = ProcessingContextContract(case_id="CASE-RAG-1", evidence_id="EVID-RAG-1", pipeline_stage="knowledge_graph")
    payload = {
        "nodes": [
            {
                "node_id": "ND-LOC-1",
                "node_type": "LOCATION",
                "label": "Location Node",
                "properties": [
                    {
                        "key": "occurred_at",
                        "value": "2026-08-01T10:05:00Z",
                        "confidence": 0.95,
                        "source_reference": {
                            "evidence_id": "EVID-RAG-1",
                            "file_path": "mock.txt",
                            "page_number": 1,
                            "parser": "test",
                            "parser_version": "1.0.0",
                            "source_element": "OCR"
                        }
                    }
                ]
            }
        ]
    }
    return AgentResultContract(
        agent="knowledge_graph_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={},
        warnings=[],
        errors=[]
    )

@pytest.fixture
def timeline_result_contract() -> AgentResultContract:
    """Mock Timeline output."""
    context = ProcessingContextContract(case_id="CASE-RAG-1", evidence_id="EVID-RAG-1", pipeline_stage="timeline_intelligence")
    payload = {
        "events": [
            {
                "event_id": "EVT-1",
                "event_type": "FILE_CREATED",
                "title": "Created",
                "original_timestamp": "2026-08-01T10:00:00Z",
                "normalized_timestamp_utc": "2026-08-01T10:00:00Z",
                "confidence": 1.0,
                "source_references": [
                    {
                        "evidence_id": "EVID-RAG-1",
                        "file_path": "mock.txt",
                        "page_number": 1,
                        "parser": "test",
                        "parser_version": "1.0.0",
                        "source_element": "OCR"
                    }
                ]
            }
        ]
    }
    return AgentResultContract(
        agent="timeline_intelligence_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={},
        warnings=[],
        errors=[]
    )

@pytest.fixture
def correlation_result_contract() -> AgentResultContract:
    """Mock Correlation output."""
    context = ProcessingContextContract(case_id="CASE-RAG-1", evidence_id="EVID-RAG-1", pipeline_stage="cross_evidence_correlation")
    payload = {
        "clusters": [
            {
                "cluster_id": "CLUST-1",
                "cluster_name": "Cluster 1",
                "matched_evidence": ["EVID-RAG-1"],
                "confidence": 1.0
            }
        ]
    }
    return AgentResultContract(
        agent="cross_evidence_correlation_agent",
        status="SUCCESS",
        processing_context=context,
        payload=payload,
        metrics={},
        warnings=[],
        errors=[]
    )
