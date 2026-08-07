# -*- coding: utf-8 -*-
"""WhatsApp export text parser."""

import re
import uuid
from typing import Tuple, List, Dict, Any
from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.exceptions import ParserFailureError
from backend.agents.document_intelligence.schema import (
    Page, Table, FormField, ExtractedTextBlock, SourceReference, DocumentElementType, Paragraph
)

class WhatsAppParser(BaseParser):
    """Parses exported chat text lines into conversational messages."""
    
    # Matches: [18/07/2026, 14:32:01] John: Hello or 18/07/2026, 14:32 - John: Hello
    _CHAT_LINE_REGEX = re.compile(
        r"^(?:\[?(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s*(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\]?\s*-\s*|\[?(?P<date2>\d{1,2}/\d{1,2}/\d{2,4}),\s*(?P<time2>\d{1,2}:\d{2}(?::\d{2})?)\]?\s*)(?P<author>[^:]+):\s*(?P<message>.+)$"
    )

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
                content_lines = f.readlines()
                
            page_num = 1
            paragraphs_list: List[Paragraph] = []
            flat_strings = []
            
            for raw_line in content_lines:
                line = raw_line.strip()
                if not line:
                    continue
                    
                match = self._CHAT_LINE_REGEX.match(line)
                if match:
                    # Message segment
                    msg_text = f"[{match.group('date') or match.group('date2')} {match.group('time') or match.group('time2')}] {match.group('author')}: {match.group('message')}"
                else:
                    msg_text = line
                    
                flat_strings.append(msg_text)
                
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="WhatsAppParser",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                
                raw_blocks.append(
                    ExtractedTextBlock(
                        text=msg_text,
                        reading_order_index=reading_order_counter,
                        source_reference=ref
                    )
                )
                
                paragraphs_list.append(
                    Paragraph(
                        paragraph_id=str(uuid.uuid4()),
                        page_number=page_num,
                        text=msg_text,
                        reading_order=reading_order_counter
                    )
                )
                reading_order_counter += 1
                
            pages.append(
                Page(
                    page_number=page_num,
                    text_content="\n".join(flat_strings),
                    paragraphs=paragraphs_list,
                    tables=[],
                    forms=[]
                )
            )
            
            return pages, tables, forms, raw_blocks
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing WhatsApp chat logs: {e}")
