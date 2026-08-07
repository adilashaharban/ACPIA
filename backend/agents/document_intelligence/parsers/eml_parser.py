# -*- coding: utf-8 -*-
"""EML email document parser."""

import email
from email import policy
import uuid
from typing import Tuple, List, Dict, Any
from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.exceptions import ParserFailureError
from backend.agents.document_intelligence.schema import (
    Page, Table, FormField, ExtractedTextBlock, SourceReference, DocumentElementType, Paragraph
)

class EMLParser(BaseParser):
    """Parses email EML files extracting header metadata fields and plain body text."""
    
    def parse(
        self, 
        file_path: str, 
        evidence_id: str
    ) -> Tuple[List[Page], List[Table], List[FormField], List[ExtractedTextBlock]]:
        pages: List[Page] = []
        tables: List[Table] = []
        forms: List[FormField] = []
        raw_blocks: List[ExtractedTextBlock] = []
        
        reading_order_counter = 0
        
        try:
            with open(file_path, "rb") as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
                
            page_num = 1
            paragraphs_list: List[Paragraph] = []
            flat_strings = []
            
            # 1. Parse headers
            headers = ["From", "To", "Subject", "Date"]
            for h in headers:
                val = msg.get(h)
                if val:
                    header_line = f"{h}: {val}"
                    flat_strings.append(header_line)
                    
                    ref = SourceReference(
                        evidence_id=evidence_id,
                        file_path=file_path,
                        page_number=page_num,
                        parser="EMLParser",
                        parser_version="1.0.0",
                        source_element=DocumentElementType.HEADER
                    )
                    
                    raw_blocks.append(
                        ExtractedTextBlock(
                            text=header_line,
                            reading_order_index=reading_order_counter,
                            source_reference=ref
                        )
                    )
                    
                    paragraphs_list.append(
                        Paragraph(
                            paragraph_id=str(uuid.uuid4()),
                            page_number=page_num,
                            text=header_line,
                            reading_order=reading_order_counter
                        )
                    )
                    reading_order_counter += 1
                    
            # 2. Extract plain text body
            body_part = msg.get_body(preferencelist=('plain',))
            body_text = ""
            if body_part:
                body_text = body_part.get_content()
                
            # If body plain is missing, fall back to walking parts
            if not body_text:
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body_text = part.get_content()
                        break
                        
            if body_text:
                flat_strings.append(body_text)
                
                # Split body text into paragraphs
                body_blocks = body_text.split("\n\n")
                for block in body_blocks:
                    block_clean = block.strip()
                    if not block_clean:
                        continue
                        
                    ref = SourceReference(
                        evidence_id=evidence_id,
                        file_path=file_path,
                        page_number=page_num,
                        parser="EMLParser",
                        parser_version="1.0.0",
                        source_element=DocumentElementType.PARAGRAPH
                    )
                    
                    raw_blocks.append(
                        ExtractedTextBlock(
                            text=block_clean,
                            reading_order_index=reading_order_counter,
                            source_reference=ref
                        )
                    )
                    
                    paragraphs_list.append(
                        Paragraph(
                            paragraph_id=str(uuid.uuid4()),
                            page_number=page_num,
                            text=block_clean,
                            reading_order=reading_order_counter
                        )
                    )
                    reading_order_counter += 1
                    
            pages.append(
                Page(
                    page_number=page_num,
                    text_content="\n\n".join(flat_strings),
                    paragraphs=paragraphs_list,
                    tables=[],
                    forms=[]
                )
            )
            
            return pages, tables, forms, raw_blocks
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing EML file: {e}")
