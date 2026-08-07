# -*- coding: utf-8 -*-
"""Document structure validator."""

import hashlib
from pathlib import Path
from typing import List, Any
from backend.agents.document_intelligence.exceptions import ChecksumMismatchError, ParserFailureError
from backend.agents.document_intelligence.schema import DocumentValidation, Page, Table

class DocumentValidator:
    """Verifies document structure and file integrity matching."""
    
    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies that the target file matches the ingestion checksum.
        
        Args:
            file_path: Physical file path.
            expected_sha256: Ingestion hash.
            
        Raises:
            ChecksumMismatchError: If hashes differ.
            ParserFailureError: If file is missing or unreadable.
        """
        path = Path(file_path)
        if not path.exists():
            raise ParserFailureError(f"Target document missing at verification path: {file_path}")
            
        try:
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            calculated = hasher.hexdigest()
            
            if calculated != expected_sha256:
                raise ChecksumMismatchError(
                    f"Integrity check failed. Expected: {expected_sha256}, Got: {calculated}",
                    details={"file_path": file_path, "expected": expected_sha256, "calculated": calculated}
                )
        except ChecksumMismatchError:
            raise
        except Exception as e:
            raise ParserFailureError(f"Integrity verification processing crash: {e}")

    @staticmethod
    def validate_structure(pages: List[Page], tables: List[Table]) -> DocumentValidation:
        """Inspects pages, cells, and bounding boxes to identify warnings.
        
        Args:
            pages: Parsed pages.
            tables: Parsed tables.
            
        Returns:
            DocumentValidation schema.
        """
        warnings: List[str] = []
        errors: List[str] = []
        
        # 1. Page count check
        if len(pages) == 0:
            warnings.append("Document structure is empty; no pages were resolved.")
            
        # 2. Table cell sanity check
        for table in tables:
            expected_cells = table.rows_count * table.cols_count
            if len(table.cells) != expected_cells:
                warnings.append(
                    f"Table {table.table_id} page {table.page_number} cells count mismatch. "
                    f"Expected: {expected_cells}, Got: {len(table.cells)}"
                )
                
        return DocumentValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
