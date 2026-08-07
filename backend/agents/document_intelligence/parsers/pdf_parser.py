# -*- coding: utf-8 -*-
"""PDF document parser using pdfplumber."""

import uuid
from typing import Tuple, List, Dict, Any
import pdfplumber
from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.exceptions import ParserFailureError
from backend.agents.document_intelligence.schema import (
    Page, Table, Cell, FormField, ExtractedTextBlock, SourceReference, DocumentElementType, BoundingBox
)

class PDFParser(BaseParser):
    """Parses PDF structures extracting textual strings, reading order, and tabular grids."""
    
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
            with pdfplumber.open(file_path) as pdf:
                for idx, pdf_page in enumerate(pdf.pages):
                    page_num = idx + 1
                    
                    # 1. Extract raw text
                    text_content = pdf_page.extract_text() or ""
                    
                    # 2. Extract tables
                    page_tables: List[Table] = []
                    extracted_tables = pdf_page.extract_tables()
                    for t_idx, ext_table in enumerate(extracted_tables):
                        table_id = str(uuid.uuid4())
                        cells: List[Cell] = []
                        
                        rows_count = len(ext_table)
                        cols_count = len(ext_table[0]) if rows_count > 0 else 0
                        
                        for r_idx, row in enumerate(ext_table):
                            for c_idx, cell_val in enumerate(row):
                                cell_text = str(cell_val or "").strip()
                                cell_ref = SourceReference(
                                    evidence_id=evidence_id,
                                    file_path=file_path,
                                    page_number=page_num,
                                    parser="PDFParser",
                                    parser_version="1.0.0",
                                    source_element=DocumentElementType.TABLE_CELL
                                )
                                cells.append(
                                    Cell(
                                        text=cell_text,
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
                            headers=[str(h or "") for h in ext_table[0]] if rows_count > 0 else [],
                            reading_order=reading_order_counter
                        )
                        tables.append(table_obj)
                        page_tables.append(table_obj)
                        reading_order_counter += 1
                        
                    # 3. Create linear text blocks for lines/paragraphs
                    # Split text by double newline to segment paragraphs
                    paragraphs_list = []
                    para_blocks = text_content.split("\n\n")
                    for p_idx, para_text in enumerate(para_blocks):
                        para_cleaned = para_text.strip()
                        if not para_cleaned:
                            continue
                            
                        block_ref = SourceReference(
                            evidence_id=evidence_id,
                            file_path=file_path,
                            page_number=page_num,
                            parser="PDFParser",
                            parser_version="1.0.0",
                            source_element=DocumentElementType.PARAGRAPH
                        )
                        raw_blocks.append(
                            ExtractedTextBlock(
                                text=para_cleaned,
                                reading_order_index=reading_order_counter,
                                source_reference=block_ref
                            )
                        )
                        from backend.agents.document_intelligence.schema import Paragraph
                        paragraphs_list.append(
                            Paragraph(
                                paragraph_id=str(uuid.uuid4()),
                                page_number=page_num,
                                text=para_cleaned,
                                reading_order=reading_order_counter
                            )
                        )
                        reading_order_counter += 1
                        
                    pages.append(
                        Page(
                            page_number=page_num,
                            text_content=text_content,
                            paragraphs=paragraphs_list,
                            tables=page_tables,
                            forms=[]
                        )
                    )
                    
            return pages, tables, forms, raw_blocks
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing PDF document: {e}")
