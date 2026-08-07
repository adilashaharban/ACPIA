# -*- coding: utf-8 -*-
"""CSV document parser using pandas."""

import uuid
from typing import Tuple, List, Dict, Any
import pandas as pd
from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.exceptions import ParserFailureError
from backend.agents.document_intelligence.schema import (
    Page, Table, Cell, FormField, ExtractedTextBlock, SourceReference, DocumentElementType
)

class CSVParser(BaseParser):
    """Parses text CSV documents, generating structured Table models."""
    
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
            # Load CSV into DataFrame
            df = pd.read_csv(file_path, header=None)
            
            page_num = 1
            table_id = str(uuid.uuid4())
            cells: List[Cell] = []
            
            rows_count = len(df)
            cols_count = len(df.columns) if rows_count > 0 else 0
            
            # Formulate text lines
            lines_content = []
            
            for r_idx in range(rows_count):
                row_items = []
                for c_idx in range(cols_count):
                    val = str(df.iloc[r_idx, c_idx] if pd.notna(df.iloc[r_idx, c_idx]) else "").strip()
                    row_items.append(val)
                    
                    cell_ref = SourceReference(
                        evidence_id=evidence_id,
                        file_path=file_path,
                        page_number=page_num,
                        parser="CSVParser",
                        parser_version="1.0.0",
                        source_element=DocumentElementType.TABLE_CELL
                    )
                    cells.append(
                        Cell(
                            text=val,
                            row_index=r_idx,
                            col_index=c_idx,
                            source_reference=cell_ref
                        )
                    )
                    
                row_str = ", ".join(row_items)
                lines_content.append(row_str)
                
                block_ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=page_num,
                    parser="CSVParser",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.TABLE
                )
                raw_blocks.append(
                    ExtractedTextBlock(
                        text=row_str,
                        reading_order_index=reading_order_counter,
                        source_reference=block_ref
                    )
                )
                reading_order_counter += 1
                
            table_obj = Table(
                table_id=table_id,
                page_number=page_num,
                rows_count=rows_count,
                cols_count=cols_count,
                cells=cells,
                headers=[str(h) for h in df.iloc[0].tolist()] if rows_count > 0 else [],
                reading_order=reading_order_counter
            )
            tables.append(table_obj)
            
            pages.append(
                Page(
                    page_number=page_num,
                    text_content="\n".join(lines_content),
                    paragraphs=[],
                    tables=[table_obj],
                    forms=[]
                )
            )
            
            return pages, tables, forms, raw_blocks
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing CSV document: {e}")
