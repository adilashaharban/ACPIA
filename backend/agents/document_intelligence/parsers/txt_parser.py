# -*- coding: utf-8 -*-
"""Plain text document parser."""

import uuid
from typing import Tuple, List, Dict, Any
from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.exceptions import ParserFailureError
from backend.agents.document_intelligence.schema import (
    Page, Table, FormField, ExtractedTextBlock, SourceReference, DocumentElementType, Paragraph
)

class TXTParser(BaseParser):
    """Parses plain text files into single-page layout structures."""
    
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
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                
            page_num = 1
            paragraphs_list: List[Paragraph] = []
            
            # Segment into lines/paragraphs by double newline
            lines = content.split("\n\n")
            for line in lines:
                text = line.strip()
                if not text:
                    continue
                    
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="TXTParser",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                
                raw_blocks.append(
                    ExtractedTextBlock(
                        text=text,
                        reading_order_index=reading_order_counter,
                        source_reference=ref
                    )
                )
                
                paragraphs_list.append(
                    Paragraph(
                        paragraph_id=str(uuid.uuid4()),
                        page_number=page_num,
                        text=text,
                        reading_order=reading_order_counter
                    )
                )
                reading_order_counter += 1
                
            pages.append(
                Page(
                    page_number=page_num,
                    text_content=content,
                    paragraphs=paragraphs_list,
                    tables=[],
                    forms=[]
                )
            )
            
            return pages, tables, forms, raw_blocks
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing text file: {e}")
