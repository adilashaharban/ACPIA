# -*- coding: utf-8 -*-
"""Document metadata extractor using PyPDF2."""

from datetime import datetime, timezone
from typing import Optional
from PyPDF2 import PdfReader
from backend.agents.metadata.exceptions import ParserFailureError
from backend.agents.metadata.schema import DocumentMetadata

class DocumentExtractor:
    """Extracts properties, author credentials, page count, and encryption markers from PDFs."""
    
    @staticmethod
    def _parse_pdf_date(date_str: str) -> Optional[datetime]:
        """Parses PDF creation dates formatted as D:YYYYMMDDHHmmSSOHH'mm'."""
        if not date_str:
            return None
        try:
            # Clean PDF date header
            if date_str.startswith("D:"):
                date_str = date_str[2:]
            # Standardize date block
            clean_str = date_str.replace("'", "").replace("Z", "")
            core_date = clean_str[:14] # YYYYMMDDHHMMSS
            
            # Pad if shorter than expected format length
            if len(core_date) < 14:
                core_date = core_date.ljust(14, "0")
                
            dt = datetime.strptime(core_date, "%Y%m%d%H%M%S")
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None

    @classmethod
    def extract(cls, file_path: str) -> DocumentMetadata:
        """Parses PDF properties.
        
        Args:
            file_path: Absolute string path.
            
        Returns:
            DocumentMetadata schema.
            
        Raises:
            ParserFailureError: If file is not a valid PDF or reading fails.
        """
        try:
            reader = PdfReader(file_path)
            encrypted = reader.is_encrypted
            
            # Read pages safely
            try:
                page_count = len(reader.pages)
            except Exception:
                page_count = 0
                
            author = None
            title = None
            creator = None
            creation_date = None
            
            if not encrypted:
                try:
                    meta = reader.metadata
                    if meta:
                        author = meta.author
                        title = meta.title
                        creator = meta.creator
                        
                        # Handle creation date tags
                        date_raw = meta.get("/CreationDate")
                        if date_raw:
                            creation_date = cls._parse_pdf_date(date_raw)
                except Exception:
                    # Ignore internal metadata parsing warnings if reading is partially broken
                    pass
                    
            return DocumentMetadata(
                page_count=page_count,
                author=author,
                title=title,
                creation_date=creation_date,
                creator=creator,
                encrypted=encrypted
            )
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing document file: {e}")
