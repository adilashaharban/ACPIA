# -*- coding: utf-8 -*-
"""Unit tests for KeywordIndex."""

from datetime import datetime, timezone
from backend.agents.rag.keyword_index import KeywordIndex
from backend.agents.rag.schema import RetrievalChunk, EmbeddingInformation, ChunkType, RetrievalSource
from backend.schemas.common import SourceReference, DocumentElementType

def test_keyword_index() -> None:
    """Verifies BM25 lexical keyword scores ranking."""
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
    
    c1 = RetrievalChunk(
        chunk_id="CHK-1",
        evidence_id="EVID-1",
        chunk_type=ChunkType.DOCUMENT,
        text="The suspect went to the store",
        embedding_id="EMB-1",
        embedding=emb_info,
        token_count=6,
        source=source
    )
    
    c2 = RetrievalChunk(
        chunk_id="CHK-2",
        evidence_id="EVID-1",
        chunk_type=ChunkType.DOCUMENT,
        text="An email was sent from laptop",
        embedding_id="EMB-2",
        embedding=emb_info,
        token_count=6,
        source=source
    )
    
    idx = KeywordIndex()
    idx.add_chunks([c1, c2])
    
    res = idx.search("suspect store", 10)
    assert len(res) == 2
    assert res[0][0].chunk_id == "CHK-1"
    assert res[0][1] > 0.0
