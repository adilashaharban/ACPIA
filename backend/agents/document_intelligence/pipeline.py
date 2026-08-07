# -*- coding: utf-8 -*-
"""Document Intelligence processing pipeline."""

import time
from typing import Tuple, List, Dict, Any, Optional
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract, EvidencePackageContract
from backend.agents.document_intelligence.dispatcher import DocumentDispatcher
from backend.agents.document_intelligence.normalizer import DocumentNormalizer
from backend.agents.document_intelligence.validator import DocumentValidator
from backend.agents.document_intelligence.metrics import DocumentMetricsCalculator
from backend.agents.document_intelligence.ocr import OCREngine, SimulatedOCREngine
from backend.agents.document_intelligence.constants import OCR_WORD_THRESHOLD_PER_PAGE
from backend.agents.document_intelligence.schema import (
    DocumentPackage, Page, Table, FormField, ExtractedTextBlock, DocumentStructure, SourceReference, DocumentElementType
)
from backend.agents.document_intelligence.exceptions import DocumentParsingError

logger = get_logger("agents.document_intelligence.pipeline")

class DocumentIntelligencePipeline:
    """Orchestrates layout-independent parsing and visual text extraction workflows."""
    
    def __init__(
        self,
        dispatcher: DocumentDispatcher,
        validator: DocumentValidator,
        normalizer: DocumentNormalizer,
        metrics_calculator: DocumentMetricsCalculator,
        ocr_engine: Optional[OCREngine] = None
    ) -> None:
        """Initializes pipeline dependencies.
        
        Args:
            dispatcher: Parser dispatcher.
            validator: File integrity validator.
            normalizer: Spacing normalizer.
            metrics_calculator: Completeness metric calculator.
            ocr_engine: OCR character recognition scanner.
        """
        self.dispatcher = dispatcher
        self.validator = validator
        self.normalizer = normalizer
        self.metrics_calculator = metrics_calculator
        self.ocr_engine = ocr_engine or SimulatedOCREngine()

    def execute(
        self,
        metadata_result: AgentResultContract
    ) -> Tuple[DocumentPackage, List[str]]:
        """Executes document parsing.
        
        Args:
            metadata_result: Result wrapper from the Metadata Agent.
            
        Returns:
            Tuple containing (DocumentPackage, warnings list).
            
        Raises:
            DocumentParsingError: On fatal checksum or parser failure.
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        
        logger.info("Document Intelligence pipeline started.")
        
        # 1. Parse Metadata result contract payload
        meta_payload = metadata_result.payload
        if not meta_payload:
            raise DocumentParsingError("Input metadata result contract is empty.")
            
        evidence_id = meta_payload.get("evidence_id")
        
        # We need to reconstruct/find the file path and ingestion hash
        # To do so, we read metadata's file_specs section
        file_specs = meta_payload.get("file_specs")
        if not file_specs:
            raise DocumentParsingError("Metadata package is missing 'file_specs' section.")
            
        # Re-verify against original evidence metadata from context
        # In a coordinate context, we locate the file_path
        from backend.database.session import get_db_context
        from backend.database.repositories.evidence_repository import EvidenceRepository
        
        file_path = None
        expected_hash = None
        mime_type = None
        
        with get_db_context() as db:
            repo = EvidenceRepository(db)
            db_evidence = repo.get_by_id(evidence_id)
            if not db_evidence:
                raise DocumentParsingError(f"Evidence {evidence_id} not registered in database.")
            file_path = db_evidence.file_path
            expected_hash = db_evidence.sha256_hash
            mime_type = db_evidence.mime_type
            
        # 2. Checksum validation
        logger.info(f"Verifying integrity checksum: {file_path}")
        self.validator.verify_integrity(file_path, expected_hash)
        logger.info("Integrity checksum verified.")
        
        # 3. Select parser dispatcher
        parser_cls = self.dispatcher.select_parser(mime_type, file_path)
        parser = parser_cls()
        logger.info(f"Parser selected: {parser_cls.__name__} for MIME {mime_type}")
        
        # 4. Extract Text programmatically
        pages, tables, forms, raw_blocks = parser.parse(file_path, evidence_id)
        
        # 5. Check if OCR is required per page
        ocr_triggered = False
        ocr_page_count = 0
        
        for page in pages:
            # Count words on page
            words_count = len(page.text_content.split())
            if words_count < OCR_WORD_THRESHOLD_PER_PAGE:
                logger.info(f"Page {page.page_number} word count ({words_count}) is below threshold. Triggering OCR...")
                ocr_triggered = True
                ocr_page_count += 1
                
                # Execute OCR blocks
                ocr_blocks = self.ocr_engine.run_ocr(file_path, page.page_number, evidence_id)
                
                # Append text contents
                ocr_text = "\n".join([block.text for block in ocr_blocks])
                page.text_content = (page.text_content + "\n" + ocr_text).strip()
                
                # Append raw blocks list
                for block in ocr_blocks:
                    text_ref = SourceReference(
                        evidence_id=evidence_id,
                        file_path=file_path,
                        page_number=page.page_number,
                        parser=self.ocr_engine.engine_name,
                        parser_version=self.ocr_engine.version,
                        source_element=DocumentElementType.OCR,
                        bounding_box=block.bounding_box
                    )
                    raw_blocks.append(
                        ExtractedTextBlock(
                            text=block.text,
                            reading_order_index=len(raw_blocks),
                            text_confidence=block.ocr_confidence,
                            layout_confidence=1.0,
                            source_reference=text_ref
                        )
                    )
                    
        # 6. Normalize text block elements
        logger.info("Normalizing character spacings...")
        raw_blocks = self.normalizer.normalize_blocks(raw_blocks)
        for page in pages:
            page.text_content = self.normalizer.normalize_whitespace(page.text_content)
            for para in page.paragraphs:
                para.text = self.normalizer.normalize_whitespace(para.text)
                
        # 7. Validate structures
        logger.info("Validating document structures...")
        validation_meta = self.validator.validate_structure(pages, tables)
        warnings.extend(validation_meta.warnings)
        
        # 8. Compute metrics
        logger.info("Computing metrics and language profiles...")
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        stats, metrics, lang_info, summary = self.metrics_calculator.calculate(
            mime_type=mime_type,
            parser_name=parser_cls.__name__,
            pages=pages,
            tables=tables,
            forms=forms,
            ocr_triggered=ocr_triggered,
            ocr_page_count=ocr_page_count,
            processing_time_ms=elapsed_ms
        )
        
        structure = DocumentStructure(
            pages=pages,
            sections=[]
        )
        
        package = DocumentPackage(
            schema_version="1.0.0",
            evidence_id=evidence_id,
            summary=summary,
            structure=structure,
            statistics=stats,
            language=lang_info,
            validation=validation_meta,
            metrics=metrics,
            raw_blocks=raw_blocks
        )
        
        logger.info("Document package built successfully.")
        return package, warnings
export_pipeline = DocumentIntelligencePipeline
