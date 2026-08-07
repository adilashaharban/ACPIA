# -*- coding: utf-8 -*-
"""Unit tests for OCREngine."""

from backend.agents.document_intelligence.ocr import SimulatedOCREngine

def test_simulated_ocr_engine() -> None:
    """Verifies that the SimulatedOCREngine returns mock text blocks with bounding boxes."""
    engine = SimulatedOCREngine()
    blocks = engine.run_ocr(
        file_path="scanned.pdf",
        page_number=1,
        evidence_id="EVID-10"
    )
    
    assert len(blocks) == 1
    block = blocks[0]
    assert block.page_number == 1
    assert block.ocr_engine == "SimulatedOCR"
    assert block.bounding_box.x0 == 10.0
    assert block.bounding_box.y1 == 80.0
    assert "[Scanned Evidence" in block.text
