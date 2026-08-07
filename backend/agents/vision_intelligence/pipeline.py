# -*- coding: utf-8 -*-
"""Vision Intelligence pipeline orchestration."""

import time
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
from PIL import Image
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract
from backend.agents.vision_intelligence.dispatcher import VisionDispatcher
from backend.agents.vision_intelligence.normalizer import VisionNormalizer
from backend.agents.vision_intelligence.validator import VisionValidator
from backend.agents.vision_intelligence.metrics import VisionMetricsCalculator
from backend.agents.vision_intelligence.exceptions import VisionParsingError
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.vision_intelligence.schema import (
    VisionPackage, VisionSummary, SceneInformation, SceneType, ImageQuality, ColorInformation,
    VisualStatistics, DetectorExecution, DetectedObject, DetectedPerson, DetectedFace,
    DetectedVehicle, DetectedLicensePlate, OCRRegion, VisualFeature
)

logger = get_logger("agents.vision_intelligence.pipeline")

class VisionIntelligencePipeline:
    """Orchestrates image processing, quality analysis, and multi-detector execution flows."""
    
    def __init__(
        self,
        dispatcher: VisionDispatcher,
        validator: VisionValidator,
        normalizer: VisionNormalizer,
        metrics_calculator: VisionMetricsCalculator
    ) -> None:
        self.dispatcher = dispatcher
        self.validator = validator
        self.normalizer = normalizer
        self.metrics_calculator = metrics_calculator

    def execute(
        self,
        metadata_result: AgentResultContract
    ) -> Tuple[VisionPackage, List[str]]:
        """Executes vision analysis.
        
        Args:
            metadata_result: Output from Metadata Agent.
            
        Returns:
            Tuple containing (VisionPackage, warnings list).
            
        Raises:
            VisionParsingError: For fatal checksum or file processing failures.
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        
        logger.info("Vision Intelligence pipeline started.")
        
        meta_payload = metadata_result.payload
        if not meta_payload:
            raise VisionParsingError("Input metadata payload is empty.")
            
        evidence_id = meta_payload.get("evidence_id")
        
        # 1. Fetch paths from database context
        from backend.database.session import get_db_context
        from backend.database.repositories.evidence_repository import EvidenceRepository
        
        file_path = None
        expected_hash = None
        mime_type = None
        
        with get_db_context() as db:
            repo = EvidenceRepository(db)
            db_evidence = repo.get_by_id(evidence_id)
            if not db_evidence:
                raise VisionParsingError(f"Evidence {evidence_id} not registered in database.")
            file_path = db_evidence.file_path
            expected_hash = db_evidence.sha256_hash
            mime_type = db_evidence.mime_type
            
        # 2. Checksum validation
        logger.info(f"Verifying integrity checksum: {file_path}")
        self.validator.verify_integrity(file_path, expected_hash)
        logger.info("Integrity checksum verified.")
        
        # 3. Load image array using Pillow/numpy
        try:
            pil_img = Image.open(file_path)
            img_array = np.array(pil_img)
        except Exception as e:
            raise VisionParsingError(f"Failed to load visual image file at {file_path}: {e}")
            
        # 4. Dispatch active detectors
        detector_classes = self.dispatcher.get_detectors(mime_type)
        logger.info(f"Selected {len(detector_classes)} detectors to run.")
        
        # Context reference
        context_ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="VisionDispatcher",
            parser_version="1.0.0",
            source_element=DocumentElementType.OCR  # standard fallback
        )
        
        # Output collectors
        objects: List[DetectedObject] = []
        people: List[DetectedPerson] = []
        faces: List[DetectedFace] = []
        vehicles: List[DetectedVehicle] = []
        plates: List[DetectedLicensePlate] = []
        ocr_regions: List[OCRRegion] = []
        features: List[VisualFeature] = []
        
        scene_info = None
        quality_info = None
        color_info = None
        perceptual_hash_str = "0000000000000000"
        
        executions_log: List[DetectorExecution] = []
        
        for det_cls in detector_classes:
            det_start = time.perf_counter()
            status = "SUCCESS"
            
            try:
                detector = det_cls()
                det_outputs = detector.detect(img_array, context_ref)
                
                # Sort detector outputs into respective fields
                for out in det_outputs:
                    if isinstance(out, DetectedObject):
                        # Normalize coordinates
                        out.bounding_box = self.normalizer.normalize_box(out.bounding_box)
                        objects.append(out)
                    elif isinstance(out, DetectedPerson):
                        out.bounding_box = self.normalizer.normalize_box(out.bounding_box)
                        people.append(out)
                    elif isinstance(out, DetectedFace):
                        out.bounding_box = self.normalizer.normalize_box(out.bounding_box)
                        faces.append(out)
                    elif isinstance(out, DetectedVehicle):
                        out.bounding_box = self.normalizer.normalize_box(out.bounding_box)
                        vehicles.append(out)
                    elif isinstance(out, DetectedLicensePlate):
                        out.bounding_box = self.normalizer.normalize_box(out.bounding_box)
                        plates.append(out)
                    elif isinstance(out, OCRRegion):
                        out.bounding_box = self.normalizer.normalize_box(out.bounding_box)
                        ocr_regions.append(out)
                    elif isinstance(out, VisualFeature):
                        features.append(out)
                    elif isinstance(out, SceneInformation):
                        scene_info = out
                    elif isinstance(out, ImageQuality):
                        quality_info = out
                    elif isinstance(out, ColorInformation):
                        color_info = out
                    elif isinstance(out, str):
                        # Perceptual hash string output from DuplicateDetector
                        perceptual_hash_str = out
                        
            except Exception as e:
                status = "FAILURE"
                warnings.append(f"Detector {det_cls.__name__} execution failure: {e}")
                
            det_time = (time.perf_counter() - det_start) * 1000.0
            executions_log.append(
                DetectorExecution(
                    detector_name=det_cls.__name__,
                    detector_version="1.0.0",
                    execution_time_ms=round(det_time, 2),
                    status=status
                )
            )
            
        # Fallbacks for mandatory sections
        if not scene_info:
            scene_info = SceneInformation(
                scene_type=SceneType.UNKNOWN,
                confidence=1.0,
                detector_name="Fallback",
                detector_version="1.0.0"
            )
            
        if not quality_info:
            quality_info = ImageQuality(
                resolution_width=img_array.shape[1] if len(img_array.shape) > 1 else 0,
                resolution_height=img_array.shape[0] if len(img_array.shape) > 0 else 0,
                aspect_ratio=1.0,
                blur_score=0.0,
                is_blurry=False,
                brightness_score=128.0,
                is_dark=False
            )
            
        if not color_info:
            color_info = ColorInformation(dominant_colors=["#808080"])
            
        # 5. Coordinate validation checks
        all_boxes = [x.bounding_box for x in (objects + people + faces + vehicles + plates + ocr_regions)]
        validation_meta = self.validator.validate_detections(all_boxes)
        warnings.extend(validation_meta.warnings)
        
        # 6. Statistics
        statistics = VisualStatistics(
            object_count=len(objects),
            person_count=len(people),
            face_count=len(faces),
            vehicle_count=len(vehicles),
            ocr_region_count=len(ocr_regions)
        )
        
        # 7. Summary
        summary = VisionSummary(
            mime_type=mime_type,
            has_faces=len(faces) > 0,
            has_vehicles=len(vehicles) > 0,
            has_text=len(ocr_regions) > 0,
            perceptual_hash=perceptual_hash_str,
            duplicate_group_id=f"GRP-{perceptual_hash_str[:8]}"
        )
        
        # 8. Compile metrics
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = self.metrics_calculator.calculate(elapsed_ms, executions_log)
        
        package = VisionPackage(
            schema_version="1.0.0",
            evidence_id=evidence_id,
            summary=summary,
            objects=objects,
            people=people,
            faces=faces,
            vehicles=vehicles,
            plates=plates,
            ocr_regions=ocr_regions,
            features=features,
            scene=scene_info,
            quality=quality_info,
            colors=color_info,
            statistics=statistics,
            validation=validation_meta,
            metrics=metrics
        )
        
        logger.info("Vision package built successfully.")
        return package, warnings
export_pipeline = VisionIntelligencePipeline
