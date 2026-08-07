# -*- coding: utf-8 -*-
"""Pytest fixtures for Investigation Reasoning Agent."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import pytest
from backend.database.base import Base
from backend.agents.base import AgentResultContract
from backend.agents.investigation_reasoning.schema import InvestigationRequest
from backend.agents.rag.schema import (
    RetrievalPackage, RetrievalRequest, RetrievalContext, RetrievedChunk,
    RetrievalStatistics, RetrievalValidation, RetrievalMetrics, RetrievalSummary,
    RetrievalChunk, ChunkType, EmbeddingInformation, RetrievalSource
)
from backend.schemas.common import SourceReference, DocumentElementType

@pytest.fixture(autouse=True)
def setup_db_context(monkeypatch, tmp_path: Path):
    """Mocks database connection."""
    db_url = f"sqlite:///{tmp_path / 'test_reasoning_acpia.db'}"
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
    evidence_id = "EVID-REAS-1"
    case_id = "CASE-REAS-1"
    
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
def mock_retrieval_package() -> RetrievalPackage:
    """Mock RAG RetrievalPackage containing parsed context chunks."""
    ref = SourceReference(
        evidence_id="EVID-REAS-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    emb_info = EmbeddingInformation(
        model_name="test",
        model_version="1.0.0",
        embedding_dimension=128,
        created_at=datetime.now(timezone.utc)
    )
    
    source = RetrievalSource(
        agent_name="test",
        package_version="1.0.0",
        evidence_id="EVID-REAS-1",
        source_reference=ref
    )
    
    c = RetrievalChunk(
        chunk_id="CHK-1",
        evidence_id="EVID-REAS-1",
        chunk_type=ChunkType.DOCUMENT,
        text="Sample text showing suspect visited store",
        embedding_id="EMB-1",
        embedding=emb_info,
        token_count=6,
        source=source
    )
    
    req = RetrievalRequest(
        request_id="REQ-1",
        query="suspect",
        retrieval_mode="HYBRID"
    )
    
    context = RetrievalContext(
        total_tokens=6,
        context_text="Sample text showing suspect visited store",
        evidence_ids=["EVID-REAS-1"],
        entity_ids=["ENT-PER-john123"]
    )
    
    from backend.agents.rag.schema import RetrievedChunk, RetrievalScore
    ret_chunk = RetrievedChunk(
        chunk=c,
        score=RetrievalScore(semantic_score=0.90, keyword_score=0.90, fused_score=0.90),
        rank=1
    )
    
    stats = RetrievalStatistics(indexed_chunks=10, retrieved_chunks=1, average_similarity=0.90)
    validation = RetrievalValidation(integrity_status="PASS")
    metrics = RetrievalMetrics(processing_time_ms=10.0, indexing_time_ms=0.0, embedding_time_ms=0.0, retrieval_time_ms=10.0)
    summary = RetrievalSummary(total_chunks=10, indexed_documents=1)
    
    return RetrievalPackage(
        schema_version="1.0.0",
        retrieval_id="RET-1",
        created_at=datetime.now(timezone.utc),
        query=req,
        context=context,
        retrieved_chunks=[ret_chunk],
        statistics=stats,
        validation=validation,
        metrics=metrics,
        summary=summary
    )

@pytest.fixture
def mock_investigation_request() -> InvestigationRequest:
    """Mock InvestigationRequest parameter."""
    from backend.agents.investigation_reasoning.schema import InvestigationRequest, InvestigationMode
    return InvestigationRequest(
        request_id="REQ-REAS-1",
        case_id="CASE-REAS-1",
        user_query="Who is the suspect?",
        retrieval_id="RET-1",
        mode=InvestigationMode.QUESTION_ANSWERING
    )
