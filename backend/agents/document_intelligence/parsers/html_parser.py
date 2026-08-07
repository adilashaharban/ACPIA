# -*- coding: utf-8 -*-
"""HTML document parser using BeautifulSoup4."""

import uuid
from typing import Tuple, List, Dict, Any
from bs4 import BeautifulSoup
from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.exceptions import ParserFailureError
from backend.agents.document_intelligence.schema import (
    Page, Table, Cell, FormField, ExtractedTextBlock, SourceReference, DocumentElementType, Paragraph
)

class HTMLParser(BaseParser):
    """Parses HTML web pages, reconstructing hierarchical text segments."""
    
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
                html_content = f.read()
                
            soup = BeautifulSoup(html_content, "html.parser")
            page_num = 1
            paragraphs_list: List[Paragraph] = []
            
            # Extract headers and body paragraphs
            tags = soup.find_all(["h1", "h2", "h3", "p", "li"])
            full_text_list = []
            
            for tag in tags:
                text = tag.get_text().strip()
                if not text:
                    continue
                    
                full_text_list.append(text)
                
                source = DocumentElementType.PARAGRAPH
                if tag.name.startswith("h"):
                    source = DocumentElementType.TITLE
                elif tag.name == "li":
                    source = DocumentElementType.LIST
                    
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="HTMLParser",
                    parser_version="1.0.0",
                    source_element=source
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
                
            # Extract HTML tables
            html_tables = soup.find_all("table")
            page_tables: List[Table] = []
            for h_table in html_tables:
                table_id = str(uuid.uuid4())
                cells: List[Cell] = []
                
                rows = h_table.find_all("tr")
                rows_count = len(rows)
                cols_count = 0
                
                headers: List[str] = []
                
                for r_idx, row in enumerate(rows):
                    cols = row.find_all(["td", "th"])
                    if r_idx == 0:
                        cols_count = len(cols)
                        headers = [c.get_text().strip() for c in cols]
                        
                    for c_idx, col in enumerate(cols):
                        col_text = col.get_text().strip()
                        cell_ref = SourceReference(
                            evidence_id=evidence_id,
                            file_path=file_path,
                            page_number=page_num,
                            parser="HTMLParser",
                            parser_version="1.0.0",
                            source_element=DocumentElementType.TABLE_CELL
                        )
                        cells.append(
                            Cell(
                                text=col_text,
                                row_index=r_idx,
                                col_index=c_idx,
                                source_reference=cell_ref
                            )
                        )
                        
                table_obj = Table(
                    table_id=table_id,
                    page_number=page_num,
                    rows_count=rows_count,
                    cols_count=cols_count,
                    cells=cells,
                    headers=headers,
                    reading_order=reading_order_counter
                )
                tables.append(table_obj)
                page_tables.append(table_obj)
                reading_order_counter += 1
                
            pages.append(
                Page(
                    page_number=page_num,
                    text_content="\n\n".join(full_text_list),
                    paragraphs=paragraphs_list,
                    tables=page_tables,
                    forms=[]
                )
            )
            
            return pages, tables, forms, raw_blocks
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing HTML file: {e}")
