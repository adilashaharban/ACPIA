# -*- coding: utf-8 -*-
"""Unit tests for Reranker and ContextBuilder."""

from datetime import datetime, timezone
from backend.agents.rag.reranker import Reranker
from backend.agents.rag.context_builder import ContextBuilder
from backend.agents.rag.schema import RetrievedChunk, RetrievalScore, RetrievalChunk, EmbeddingInformation, ChunkType, RetrievalSource
from backend.schemas.common import SourceReference, DocumentElementType

def test_reranker_and_context_builder() -> None:
    """Verifies that re-ranked candidates sort correctly and aggregate token boundaries."""
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
    
    c1 = RetrievalChunk(
        chunk_id="CHK-1",
        evidence_id="E1",
        chunk_type=ChunkType.DOCUMENT,
        text="First segment text",
        embedding_id="EMB-1",
        embedding=emb_info,
        token_count=3,
        source=source
    )
    
    c2 = RetrievalChunk(
        chunk_id="CHK-2",
        evidence_id="E1",
        chunk_type=ChunkType.DOCUMENT,
        text="Second segment text",
        embedding_id="EMB-2",
        embedding=emb_info,
        token_count=3,
        source=source
    )
    
    r1 = RetrievedChunk(
        chunk=c1,
        score=RetrievalScore(semantic_score=0.80, keyword_score=0.50, fused_score=0.65),
        rank=2
    )
    
    r2 = RetrievedChunk(
        chunk=c2,
        score=RetrievalScore(semantic_score=0.90, keyword_score=0.70, fused_score=0.80),
        rank=1
    )
    
    sorted_res = Reranker.rerank([r1, r2])
    assert sorted_res[0].chunk.chunk_id == "CHK-2"
    assert sorted_res[0].rank == 1
    
    # Context builder check
    ctx = ContextBuilder.build_context(sorted_res, token_budget=10)
    assert ctx.total_tokens == 6
    assert "CHK-2" in ctx.context_text
