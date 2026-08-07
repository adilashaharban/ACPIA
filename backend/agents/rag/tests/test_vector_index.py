# -*- coding: utf-8 -*-
"""Unit tests for VectorIndex."""

from datetime import datetime, timezone
from backend.agents.rag.vector_index import VectorIndex
from backend.agents.rag.repositories.faiss_repository import FAISSRepository
from backend.agents.rag.schema import RetrievalChunk, EmbeddingInformation, ChunkType, RetrievalSource
from backend.schemas.common import SourceReference, DocumentElementType

def test_vector_index() -> None:
    """Verifies that vector index search completes and returns sorted similarities."""
    ref = SourceReference(
        evidence_id="EVID-1",
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
        evidence_id="EVID-1",
        source_reference=ref
    )
    
    c = RetrievalChunk(
        chunk_id="CHK-1",
        evidence_id="EVID-1",
        chunk_type=ChunkType.DOCUMENT,
        text="Sample text",
        embedding_id="EMB-1",
        embedding=emb_info,
        token_count=2,
        source=source
    )
    
    repo = FAISSRepository()
    idx = VectorIndex(repo)
    idx.add_chunks([c])
    
    q_vec = [1.0] * 128
    res = idx.search(q_vec, 10)
    assert len(res) == 1
    assert res[0][0].chunk_id == "CHK-1"
    assert -1.0 <= res[0][1] <= 1.0
