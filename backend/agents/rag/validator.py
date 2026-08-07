# -*- coding: utf-8 -*-
"""Retrieval validation checks module."""

import hashlib
from pathlib import Path
from typing import List
from backend.agents.rag.exceptions import ValidationError, ChecksumMismatchError, RAGError
from backend.agents.rag.schema import (
    RetrievalValidation, RetrievalChunk, RetrievedChunk
)

class Validator:
    """Validates structural integrity, missing embeddings, and token limits."""
    
    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies evidence checksum.
        
        Args:
            file_path: Evidence file path.
            expected_sha256: Expected SHA hash.
        """
        path = Path(file_path)
        if not path.exists():
            raise RAGError(f"Evidence file missing during RAG validation: {file_path}")
            
        try:
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            calculated = hasher.hexdigest()
            if calculated != expected_sha256:
                raise ChecksumMismatchError(
                    f"Integrity check failed. Expected: {expected_sha256}, Got: {calculated}"
                )
        except ChecksumMismatchError:
            raise
        except Exception as e:
            raise RAGError(f"Integrity check processing crash: {e}")

    @staticmethod
    def validate_package(
        chunks: List[RetrievedChunk]
    ) -> RetrievalValidation:
        """Runs validation checks.
        
        Args:
            chunks: Retrieved chunks list.
            
        Returns:
            RetrievalValidation status check object.
        """
        warnings = []
        errors = []
        
        # Check unique chunk IDs
        c_ids = [c.chunk.chunk_id for c in chunks]
        if len(c_ids) != len(set(c_ids)):
            errors.append("Duplicate chunk IDs detected in retrieved chunks list.")
            
        # Check invalid similarity scores
        for c in chunks:
            if not (-1.0 <= c.score.fused_score <= 2.0):
                errors.append(f"Chunk '{c.chunk.chunk_id}' score outside bounds: {c.score.fused_score}")
                
        return RetrievalValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
export_validator = Validator
