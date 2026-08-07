# -*- coding: utf-8 -*-
"""Unit tests for HybridRetriever."""

from datetime import datetime, timezone
from backend.agents.rag.keyword_index import KeywordIndex
from backend.agents.rag.vector_index import VectorIndex
from backend.agents.rag.repositories.faiss_repository import FAISSRepository
from backend.agents.rag.hybrid_retriever import HybridRetriever
from backend.agents.rag.schema import RetrievalChunk, EmbeddingInformation, ChunkType, RetrievalSource, RetrievalMode
from backend.schemas.common import SourceReference, DocumentElementType

def test_hybrid_retriever() -> None:
    """Verifies that dense/sparse fusion merges scores correctly."""
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
        text="Unique key search suspect word",
        embedding_id="EMB-1",
        embedding=emb_info,
        token_count=5,
        source=source
    )
    
    v_idx = VectorIndex(FAISSRepository())
    v_idx.add_chunks([c])
    
    kw_idx = KeywordIndex()
    kw_idx.add_chunks([c])
    
    retriever = HybridRetriever(v_idx, kw_idx)
    q_vec = [1.0] * 128
    
    res = retriever.retrieve("suspect", q_vec, RetrievalMode.HYBRID, 10)
    assert len(res) == 1
    assert res[0].chunk.chunk_id == "CHK-1"
    assert res[0].rank == 1
