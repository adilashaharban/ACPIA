# -*- coding: utf-8 -*-
"""OCR engine wrapper abstraction."""

from abc import ABC, abstractmethod
from typing import List
from backend.agents.document_intelligence.schema import OCRBlock, BoundingBox, SourceReference, DocumentElementType

class OCREngine(ABC):
    """Abstract Base Class specifying plug-in OCR engines."""
    
    @abstractmethod
    def run_ocr(
        self, 
        file_path: str, 
        page_number: int,
        evidence_id: str
    ) -> List[OCRBlock]:
        """Runs character recognition on the given file page.
        
        Args:
            file_path: Absolute string path.
            page_number: Target page number.
            evidence_id: Evidentiary parent ID.
            
        Returns:
            A list of OCRBlock items.
        """
        pass


class SimulatedOCREngine(OCREngine):
    """Simulated OCR engine for development and CI testing environments."""
    
    def __init__(self, engine_name: str = "SimulatedOCR", version: str = "1.0.0") -> None:
        self.engine_name = engine_name
        self.version = version

    def run_ocr(
        self, 
        file_path: str, 
        page_number: int,
        evidence_id: str
    ) -> List[OCRBlock]:
        # Return a mock block representing scanned text detected on page
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=page_number,
            parser="SimulatedOCR",
            parser_version=self.version,
            source_element=DocumentElementType.OCR
        )
        return [
            OCRBlock(
                text="[Scanned Evidence Document OCR text block content.]",
                page_number=page_number,
                bounding_box=BoundingBox(x0=10.0, y0=20.0, x1=200.0, y1=80.0),
                ocr_confidence=0.98,
                ocr_engine=self.engine_name,
                ocr_engine_version=self.version,
                source_reference=ref
            )
        ]
