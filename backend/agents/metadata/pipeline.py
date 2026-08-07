# -*- coding: utf-8 -*-
"""Metadata Agent Pipeline."""

import time
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any, Optional
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract, EvidencePackageContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.metadata.dispatcher import MetadataDispatcher
from backend.agents.metadata.normalizer import MetadataNormalizer
from backend.agents.metadata.validator import MetadataValidator
from backend.agents.metadata.metrics import MetadataMetricsCalculator
from backend.agents.metadata.schema import (
    MetadataPackage,
    ImageMetadata,
    VideoMetadata,
    AudioMetadata,
    DocumentMetadata,
    FileMetadata,
)
from backend.agents.metadata.exceptions import MetadataExtractionError

logger = get_logger("agents.metadata.pipeline")

class MetadataPipeline:
    """Orchestrates the metadata extraction process for ACPIA evidence files."""
    
    def __init__(
        self,
        dispatcher: MetadataDispatcher,
        validator: MetadataValidator,
        normalizer: MetadataNormalizer,
        metrics_calculator: MetadataMetricsCalculator
    ) -> None:
        """Initializes the pipeline with injected support dependencies.
        
        Args:
            dispatcher: Ingested MIME type dispatcher.
            validator: Checksum and schema validator.
            normalizer: Data normalization module.
            metrics_calculator: Completeness calculator.
        """
        self.dispatcher = dispatcher
        self.validator = validator
        self.normalizer = normalizer
        self.metrics_calculator = metrics_calculator

    def execute(
        self,
        intake_result: AgentResultContract
    ) -> Tuple[MetadataPackage, List[str]]:
        """Executes the ingestion metadata parsing pipeline steps.
        
        Args:
            intake_result: Result wrapper from the Evidence Intake Agent.
            
        Returns:
            Tuple of (MetadataPackage, warnings list).
            
        Raises:
            MetadataExtractionError: For fatal validation or parsing errors.
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        
        logger.info("Metadata pipeline execution started.")
        
        # 1. Read input evidence package
        payload = intake_result.payload
        if not payload:
            raise MetadataExtractionError("Input result contract has an empty payload.")
            
        evidence_package = EvidencePackageContract.model_validate(payload)
        meta = evidence_package.evidence_metadata
        file_path = meta.file_path
        expected_hash = meta.sha256_hash
        mime_type = meta.mime_type
        evidence_id = meta.evidence_id
        
        # 2. Checksum validation
        logger.info(f"Verifying integrity checksum for: {file_path}")
        self.validator.verify_integrity(file_path, expected_hash)
        logger.info("Integrity checksum verification passed.")
        
        # 3. Generic metadata extraction
        logger.info("Extracting filesystem metadata...")
        from backend.agents.metadata.extractors.generic_extractor import GenericExtractor
        file_specs: FileMetadata = GenericExtractor.extract(file_path)
        
        # 4. Dispatch specialized extractor
        extractor_cls = self.dispatcher.select_extractor(mime_type)
        logger.info(f"Extractor selected: {extractor_cls.__name__} for MIME {mime_type}")
        
        # 5. Extract specialized metadata
        image_details: Optional[ImageMetadata] = None
        video_details: Optional[VideoMetadata] = None
        audio_details: Optional[AudioMetadata] = None
        document_details: Optional[DocumentMetadata] = None
        
        details_obj: Any = None
        
        if mime_type.startswith("image/"):
            logger.info("Parsing image headers...")
            image_details = extractor_cls.extract(file_path)
            details_obj = image_details
        elif mime_type.startswith("video/"):
            logger.info("Parsing video tracks...")
            video_details = extractor_cls.extract(file_path)
            details_obj = video_details
        elif mime_type.startswith("audio/"):
            logger.info("Parsing audio tracks...")
            audio_details = extractor_cls.extract(file_path)
            details_obj = audio_details
        elif mime_type == "application/pdf":
            logger.info("Parsing document metadata...")
            document_details = extractor_cls.extract(file_path)
            details_obj = document_details
            
        logger.info("Metadata extraction completed.")
        
        # 6. Normalize metadata properties
        logger.info("Normalizing extracted properties...")
        if file_specs.creation_time:
            file_specs.creation_time = self.normalizer.normalize_date(file_specs.creation_time)
        if file_specs.modification_time:
            file_specs.modification_time = self.normalizer.normalize_date(file_specs.modification_time)
            
        if image_details:
            if image_details.gps and image_details.gps.timestamp:
                image_details.gps.timestamp = self.normalizer.normalize_date(image_details.gps.timestamp)
            if image_details.camera and image_details.camera.software:
                # normalize software or other text details if needed
                pass
        elif video_details:
            video_details.video_codec = self.normalizer.normalize_codec(video_details.video_codec)
            if video_details.audio_codec:
                video_details.audio_codec = self.normalizer.normalize_codec(video_details.audio_codec)
        elif audio_details:
            audio_details.audio_codec = self.normalizer.normalize_codec(audio_details.audio_codec)
        elif document_details:
            if document_details.creation_date:
                document_details.creation_date = self.normalizer.normalize_date(document_details.creation_date)
                
        logger.info("Normalization completed.")
        
        # 7. Validate metadata
        logger.info("Validating metadata parameters consistency...")
        raw_meta = details_obj.model_dump() if details_obj else {}
        validation_meta = self.validator.validate_metadata(
            file_path=file_path,
            file_type=mime_type,
            raw_meta=raw_meta,
            image_meta=image_details
        )
        warnings.extend(validation_meta.issues_detected)
        logger.info("Validation completed.")
        
        # 8. Compute completeness metrics
        logger.info("Calculating completeness metrics...")
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Resolve mime category
        category = "generic"
        for key in ("image", "video", "audio"):
            if mime_type.startswith(f"{key}/"):
                category = key
                break
        if mime_type == "application/pdf":
            category = "document"
            
        metrics, summary = self.metrics_calculator.calculate(
            category=category,
            extractor_name=extractor_cls.__name__,
            details_obj=details_obj,
            warnings_count=len(warnings),
            processing_time_ms=elapsed_ms
        )
        logger.info("Metrics calculated.")
        
        # 9. Build standard package
        package = MetadataPackage(
            schema_version="1.0.0",
            evidence_id=evidence_id,
            summary=summary,
            file_specs=file_specs,
            image_details=image_details,
            video_details=video_details,
            audio_details=audio_details,
            document_details=document_details,
            validation=validation_meta,
            metrics=metrics,
            raw_metadata=raw_meta
        )
        
        logger.info("Metadata package built successfully.")
        return package, warnings
