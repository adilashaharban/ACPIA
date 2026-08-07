# -*- coding: utf-8 -*-
"""Vision agent candidate entity extractor."""

import uuid
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.entity_resolution.schema import CandidateEntity, EntityType, EntityAttribute

class VisionExtractor:
    """Extracts candidate entities from detected objects, plates, and features packages."""
    
    @staticmethod
    def extract(vision_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateEntity]:
        candidates: List[CandidateEntity] = []
        if not vision_payload:
            return candidates
            
        # Extract vehicle plates
        plates = vision_payload.get("plates", [])
        for plate in plates:
            ref = SourceReference(
                evidence_id=evidence_id,
                file_path=file_path,
                page_number=1,
                parser="VisionExtractor",
                parser_version="1.0.0",
                source_element=DocumentElementType.OCR
            )
            # License plate localization gives plate region candidates
            candidates.append(
                CandidateEntity(
                    candidate_id=str(uuid.uuid4()),
                    entity_type=EntityType.PLATE,
                    raw_value=plate.get("plate_id", "detected_plate"),
                    normalized_value=plate.get("plate_id", "detected_plate"),
                    confidence=plate.get("confidence", 0.90),
                    extraction_agent="vision_intelligence",
                    source_reference=ref
                )
            )
            
        # Extract visual features (dominant colors, clothing colors)
        features = vision_payload.get("features", [])
        for feat in features:
            ref = SourceReference(
                evidence_id=evidence_id,
                file_path=file_path,
                page_number=1,
                parser="VisionExtractor",
                parser_version="1.0.0",
                source_element=DocumentElementType.OCR
            )
            candidates.append(
                CandidateEntity(
                    candidate_id=str(uuid.uuid4()),
                    entity_type=EntityType.UNKNOWN,
                    raw_value=feat.get("value", ""),
                    normalized_value=feat.get("value", ""),
                    confidence=feat.get("confidence", 0.95),
                    extraction_agent="vision_intelligence",
                    source_reference=ref,
                    supporting_attributes=[
                        EntityAttribute(
                            key=feat.get("feature_type", "color"),
                            value=feat.get("value", ""),
                            confidence=feat.get("confidence", 0.95),
                            source_reference=ref
                        )
                    ]
                )
            )
            
        return candidates
export_vision_extractor = VisionExtractor
