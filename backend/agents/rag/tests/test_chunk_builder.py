# -*- coding: utf-8 -*-
"""Unit tests for ChunkBuilder."""

from backend.agents.rag.chunk_builder import ChunkBuilder
from backend.agents.rag.schema import ChunkType
from backend.schemas.common import SourceReference, DocumentElementType

def test_chunk_builder() -> None:
    """Verifies that words arrays are split into sequence chunk structures with linkages."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    extracted_items = [{
        "text": "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10",
        "chunk_type": ChunkType.DOCUMENT,
        "source_reference": ref,
        "entity_ids": ["ENT-1"]
    }]
    
    chunks = ChunkBuilder.build_chunks(
        extracted_items=extracted_items,
        model_name="test_model",
        dimension=128,
        chunk_size=4,
        chunk_overlap=2
    )
    
    # 10 words, chunk_size=4, overlap=2:
    # Chunk 1: word1 word2 word3 word4 (idx 0 to 4, advanced by 2)
    # Chunk 2: word3 word4 word5 word6 (idx 2 to 6, advanced by 2)
    # Chunk 3: word5 word6 word7 word8 (idx 4 to 8, advanced by 2)
    # Chunk 4: word7 word8 word9 word10 (idx 6 to 10)
    assert len(chunks) == 4
    assert chunks[0].next_chunk_id == chunks[1].chunk_id
    assert chunks[1].previous_chunk_id == chunks[0].chunk_id
    assert chunks[1].next_chunk_id == chunks[2].chunk_id
    assert "ENT-1" in chunks[0].source.entity_ids
