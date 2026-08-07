# -*- coding: utf-8 -*-
"""Pydantic V2 schema models for the Document Intelligence Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field
from backend.schemas.common import ACPIABaseModel

class DocumentElementType(str, Enum):
    """Supported structural elements within document layouts."""
    PARAGRAPH = "PARAGRAPH"
    TABLE = "TABLE"
    TABLE_CELL = "TABLE_CELL"
    HEADER = "HEADER"
    FOOTER = "FOOTER"
    TITLE = "TITLE"
    FORM = "FORM"
    LIST = "LIST"
    IMAGE_CAPTION = "IMAGE_CAPTION"
    OCR = "OCR"


class BoundingBox(ACPIABaseModel):
    """Geometric coordinates representing page regions."""
    x0: float = Field(..., description="Top-left x coordinate")
    y0: float = Field(..., description="Top-left y coordinate")
    x1: float = Field(..., description="Bottom-right x coordinate")
    y1: float = Field(..., description="Bottom-right y coordinate")


class SourceReference(ACPIABaseModel):
    """Complete traceability context mapping text blocks to source locations."""
    evidence_id: str = Field(..., description="Parent evidence UUID")
    file_path: str = Field(..., description="Absolute path location of the file")
    page_number: int = Field(..., description="1-indexed page index number")
    parser: str = Field(..., description="Parser class identifier")
    parser_version: str = Field(..., description="Software version version")
    source_element: DocumentElementType = Field(..., description="Structural source label")
    bounding_box: Optional[BoundingBox] = Field(default=None)


class ExtractedTextBlock(ACPIABaseModel):
    """Structured text block containing trace context."""
    text: str = Field(..., description="Raw text content parsed")
    reading_order_index: int = Field(..., description="Normalized reading flow index")
    text_confidence: float = Field(default=1.0, description="Extraction confidence")
    layout_confidence: float = Field(default=1.0, description="Layout segment confidence")
    source_reference: SourceReference = Field(..., description="Audit traceability link")


class OCRBlock(ACPIABaseModel):
    """Visual text segment extracted via OCR engine."""
    text: str = Field(..., description="Extracted word/phrase")
    page_number: int = Field(..., description="1-indexed page number")
    bounding_box: BoundingBox = Field(..., description="Spatial box")
    ocr_confidence: float = Field(..., description="OCR engine confidence score")
    ocr_engine: str = Field(..., description="OCR library name")
    ocr_engine_version: str = Field(..., description="OCR version")
    source_reference: SourceReference = Field(..., description="Audit traceability link")


class Cell(ACPIABaseModel):
    """Row-column cell item within a Table structure."""
    text: str = Field(..., description="Cell text value")
    row_index: int = Field(..., description="0-indexed row number")
    col_index: int = Field(..., description="0-indexed column number")
    source_reference: SourceReference = Field(..., description="Audit traceability link")


class Table(ACPIABaseModel):
    """Tabular layout parsed from the document page."""
    table_id: str = Field(..., description="Unique generated UUID for table")
    page_number: int = Field(..., description="Page index")
    rows_count: int = Field(..., description="Number of rows")
    cols_count: int = Field(..., description="Number of columns")
    cells: List[Cell] = Field(default_factory=list, description="All cellular items")
    headers: List[str] = Field(default_factory=list, description="Row header names")
    reading_order: int = Field(..., description="Flow order index")


class FormField(ACPIABaseModel):
    """Key-value form field pair parsed from layouts."""
    field_id: str = Field(..., description="Unique form field ID")
    page_number: int = Field(..., description="Page index")
    label: str = Field(..., description="Form label name")
    value: Optional[str] = Field(default=None, description="Form label value")
    text_confidence: float = Field(default=1.0)
    layout_confidence: float = Field(default=1.0)
    source_reference: SourceReference = Field(..., description="Audit traceability link")


class Paragraph(ACPIABaseModel):
    """Text paragraph structure."""
    paragraph_id: str = Field(..., description="Unique paragraph ID")
    page_number: int = Field(..., description="Page index")
    text: str = Field(..., description="Continuous string block")
    reading_order: int = Field(..., description="Flow order index")


class Section(ACPIABaseModel):
    """Nested logical section based on visual headers."""
    section_id: str = Field(..., description="Unique section ID")
    title: Optional[str] = Field(default=None, description="Heading title")
    paragraphs: List[Paragraph] = Field(default_factory=list, description="Linked paragraphs")


class Page(ACPIABaseModel):
    """Logical page element wrapping layout shapes."""
    page_number: int = Field(..., description="1-indexed page index")
    text_content: str = Field(..., description="Full raw string layout")
    paragraphs: List[Paragraph] = Field(default_factory=list, description="Paragraph elements")
    tables: List[Table] = Field(default_factory=list, description="Tabular shapes")
    forms: List[FormField] = Field(default_factory=list, description="Form items")


class DocumentStructure(ACPIABaseModel):
    """Reconstructed layout flows of the processed file."""
    pages: List[Page] = Field(default_factory=list, description="List of pages")
    sections: List[Section] = Field(default_factory=list, description="List of logical sections")


class DocumentStatistics(ACPIABaseModel):
    """Statistical summary of document composition."""
    char_count: int = Field(..., description="Character count")
    word_count: int = Field(..., description="Word count")
    page_count: int = Field(..., description="Total pages")
    table_count: int = Field(..., description="Total tables")
    form_field_count: int = Field(..., description="Total forms fields")
    image_count: int = Field(..., description="Total embedded image shapes")
    ocr_page_count: int = Field(..., description="Total pages processed via OCR engine")


class DocumentValidation(ACPIABaseModel):
    """Diagnostics warnings and issues detected during checks."""
    integrity_status: str = Field(default="PASS")
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ExtractionMetrics(ACPIABaseModel):
    """Performance benchmarks of the parser run."""
    parser_used: str = Field(..., description="Parser class string identifier")
    ocr_triggered: bool = Field(..., description="True if OCR was executed")
    ocr_confidence: Optional[float] = Field(default=None, description="Average OCR confidence")
    processing_time_ms: float = Field(..., description="Execution runtime")


class LanguageInformation(ACPIABaseModel):
    """Language categorization details."""
    primary_language: str = Field(..., description="Primary detected locale")
    confidence: float = Field(..., description="Language confidence score")
    detected_languages: List[str] = Field(default_factory=list, description="Bilingual/Multilingual list")


class DocumentSummary(ACPIABaseModel):
    """Mime category and parser information summary."""
    mime_type: str = Field(..., description="Verified mime type")
    is_scanned: bool = Field(..., description="True if OCR engine was main text provider")
    structure_detected: bool = Field(..., description="True if tables/forms/sections resolved")
    parser_name: str = Field(..., description="Class name")
    parser_version: str = Field(..., description="Software version")


class DocumentPackage(ACPIABaseModel):
    """Root standard Document Package payload output model."""
    schema_version: str = Field(default="1.0.0")
    evidence_id: str = Field(..., description="Target parent evidence ID")
    summary: DocumentSummary = Field(..., description="Summary details")
    structure: DocumentStructure = Field(..., description="Layout content structures")
    statistics: DocumentStatistics = Field(..., description="Statistical detail metrics")
    language: LanguageInformation = Field(..., description="Language flags")
    validation: DocumentValidation = Field(..., description="Layout warnings log")
    metrics: ExtractionMetrics = Field(..., description="Performance profile")
    raw_blocks: List[ExtractedTextBlock] = Field(default_factory=list, description="Linear textual blocks list")
