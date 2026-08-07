# -*- coding: utf-8 -*-
"""XML document parser."""

import uuid
import xml.etree.ElementTree as ET
from typing import Tuple, List, Dict, Any
from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.exceptions import ParserFailureError
from backend.agents.document_intelligence.schema import (
    Page, Table, FormField, ExtractedTextBlock, SourceReference, DocumentElementType, Paragraph
)

class XMLParser(BaseParser):
    """Parses XML structures recursively compiling element nodes into text lists."""
    
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
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            page_num = 1
            paragraphs_list: List[Paragraph] = []
            flat_strings = []
            
            def parse_node(node: ET.Element, path: str = ""):
                nonlocal reading_order_counter
                current_path = f"{path}/{node.tag}" if path else node.tag
                
                # Check text content of node
                if node.text and node.text.strip():
                    text_line = f"{current_path}: {node.text.strip()}"
                    flat_strings.append(text_line)
                    
                    ref = SourceReference(
                        evidence_id=evidence_id,
                        file_path=file_path,
                        page_number=page_num,
                        parser="XMLParser",
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
                    
                # Attributes check
                for attr_k, attr_v in node.attrib.items():
                    attr_line = f"{current_path}[@{attr_k}]: {attr_v}"
                    flat_strings.append(attr_line)
                    
                    ref = SourceReference(
                        evidence_id=evidence_id,
                        file_path=file_path,
                        page_number=page_num,
                        parser="XMLParser",
                        parser_version="1.0.0",
                        source_element=DocumentElementType.PARAGRAPH
                    )
                    
                    raw_blocks.append(
                        ExtractedTextBlock(
                            text=attr_line,
                            reading_order_index=reading_order_counter,
                            source_reference=ref
                        )
                    )
                    
                    paragraphs_list.append(
                        Paragraph(
                            paragraph_id=str(uuid.uuid4()),
                            page_number=page_num,
                            text=attr_line,
                            reading_order=reading_order_counter
                        )
                    )
                    reading_order_counter += 1
                    
                for child in node:
                    parse_node(child, current_path)
                    
            parse_node(root)
            
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
            raise ParserFailureError(f"Failed parsing XML document: {e}")
