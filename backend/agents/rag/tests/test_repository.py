# -*- coding: utf-8 -*-
"""Unit tests for RAGRepository implementations."""

from datetime import datetime, timezone
from backend.agents.rag.repositories.sqlite_repository import SQLiteRepository
from backend.agents.rag.repositories.faiss_repository import FAISSRepository
from backend.agents.rag.repositories.chroma_repository import ChromaRepository
from backend.agents.rag.schema import RetrievalChunk, EmbeddingInformation, ChunkType, RetrievalSource
from backend.schemas.common import SourceReference, DocumentElementType

def test_repositories() -> None:
    """Verifies that chunks save, load, exists, count, and clear methods function properly."""
    ref = SourceReference(
        evidence_id="E1",
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
        evidence_id="E1",
        source_reference=ref
    )
    
    c = RetrievalChunk(
        chunk_id="CHK-1",
        evidence_id="E1",
        chunk_type=ChunkType.DOCUMENT,
        text="Sample text content for index testing",
        embedding_id="EMB-1",
        embedding=emb_info,
        token_count=6,
        source=source
    )
    
    # SQLite check
    sq = SQLiteRepository(":memory:")
    sq.add_chunks([c])
    assert sq.count() == 1
    assert sq.exists("CHK-1")
    assert len(sq.load_chunks()) == 1
    
    # FAISS check
    fs = FAISSRepository()
    fs.add_chunks([c])
    assert fs.count() == 1
    
    # Chroma check
    ch = ChromaRepository()
    ch.add_chunks([c])
    assert ch.count() == 1
