# -*- coding: utf-8 -*-
"""Unit tests for Visual Detectors."""

import numpy as np
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.vision_intelligence.detectors.object_detector import ObjectDetector
from backend.agents.vision_intelligence.detectors.face_detector import FaceDetector
from backend.agents.vision_intelligence.detectors.vehicle_detector import VehicleDetector
from backend.agents.vision_intelligence.detectors.license_plate_detector import LicensePlateDetector
from backend.agents.vision_intelligence.detectors.scene_detector import SceneDetector
from backend.agents.vision_intelligence.detectors.color_detector import ColorDetector
from backend.agents.vision_intelligence.detectors.quality_detector import QualityDetector
from backend.agents.vision_intelligence.detectors.duplicate_detector import DuplicateDetector
from backend.agents.vision_intelligence.detectors.ocr_region_detector import OcrRegionDetector
from backend.agents.vision_intelligence.schema import SceneType, VehicleType, FeatureType

def test_detectors_running() -> None:
    """Verifies that all visual detector algorithms output expected types and bounding grids."""
    # 100x100 RGB image array (blue canvas)
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    img_array[:, :, 2] = 255  # Blue channel max
    
    context = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.jpg",
        page_number=1,
        parser="Test",
        parser_version="1.0.0",
        source_element=DocumentElementType.OCR
    )
    
    # 1. ObjectDetector
    obj_det = ObjectDetector()
    objs = obj_det.detect(img_array, context)
    assert len(objs) == 1
    assert objs[0].class_name == "EvidenceObjectShape"
    
    # 2. FaceDetector
    face_det = FaceDetector()
    faces = face_det.detect(img_array, context)
    assert len(faces) == 1
    
    # 3. VehicleDetector
    veh_det = VehicleDetector()
    vehs = veh_det.detect(img_array, context)
    assert len(vehs) == 1
    assert vehs[0].vehicle_type == VehicleType.CAR
    
    # 4. LicensePlateDetector
    plate_det = LicensePlateDetector()
    plates = plate_det.detect(img_array, context)
    assert len(plates) == 1
    
    # 5. SceneDetector
    scene_det = SceneDetector()
    scenes = scene_det.detect(img_array, context)
    assert len(scenes) == 1
    # Low mean brightness is INDOOR
    assert scenes[0].scene_type == SceneType.INDOOR
    
    # 6. ColorDetector
    color_det = ColorDetector()
    colors = color_det.detect(img_array, context)
    # Returns [ColorInformation, VisualFeature]
    assert len(colors) == 2
    assert colors[1].feature_type == FeatureType.COLOR
    
    # 7. QualityDetector
    qual_det = QualityDetector()
    qual = qual_det.detect(img_array, context)
    assert len(qual) == 1
    assert qual[0].resolution_width == 100
    assert qual[0].aspect_ratio == 1.0
    
    # 8. DuplicateDetector
    dup_det = DuplicateDetector()
    dups = dup_det.detect(img_array, context)
    assert len(dups) == 1
    assert len(dups[0]) == 16  # standard 16-hex perceptual hash length
    
    # 9. OcrRegionDetector
    ocr_det = OcrRegionDetector()
    ocr = ocr_det.detect(img_array, context)
    assert len(ocr) == 1
    assert ocr[0].text_present is True
