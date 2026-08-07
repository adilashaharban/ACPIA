# -*- coding: utf-8 -*-
"""JSON document parser."""

import json
import uuid
from typing import Tuple, List, Dict, Any
from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.exceptions import ParserFailureError
from backend.agents.document_intelligence.schema import (
    Page, Table, FormField, ExtractedTextBlock, SourceReference, DocumentElementType, Paragraph
)

class JSONParser(BaseParser):
    """Parses JSON files recursively translating dictionary mappings into paragraph flows."""
    
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
                data = json.load(f)
                
            page_num = 1
            paragraphs_list: List[Paragraph] = []
            flat_strings = []
            
            # Simple flattener function to string lines
            def flatten_json(obj: Any, prefix: str = ""):
                nonlocal reading_order_counter
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        new_key = f"{prefix}.{k}" if prefix else k
                        flatten_json(v, new_key)
                elif isinstance(obj, list):
                    for idx, val in enumerate(obj):
                        new_key = f"{prefix}[{idx}]"
                        flatten_json(val, new_key)
                else:
                    text_line = f"{prefix}: {obj}"
                    flat_strings.append(text_line)
                    
                    ref = SourceReference(
                        evidence_id=evidence_id,
                        file_path=file_path,
                        page_number=page_num,
                        parser="JSONParser",
                        parser_version="1.0.0",
                        source_element=DocumentElementType.PARAGRAPH
                    )
                    
                    raw_blocks.append(
                        ExtractedTextBlock(
                            text=text_line,
                            reading_order_index=reading_order_counter,
                            source_reference=ref
                        )
                    )
                    
                    paragraphs_list.append(
                        Paragraph(
                            paragraph_id=str(uuid.uuid4()),
                            page_number=page_num,
                            text=text_line,
                            reading_order=reading_order_counter
                        )
                    )
                    reading_order_counter += 1
                    
            flatten_json(data)
            
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
            raise ParserFailureError(f"Failed parsing JSON file: {e}")
