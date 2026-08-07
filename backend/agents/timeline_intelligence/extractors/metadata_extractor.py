# -*- coding: utf-8 -*-
"""Metadata timeline events extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.timeline_intelligence.schema import TimelineEventType

class MetadataExtractor:
    """Extracts timestamp candidate attributes from ingestion file specifications."""
    
    @staticmethod
    def extract(metadata_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[Dict[str, Any]]:
        candidates = []
        if not metadata_payload:
            return candidates
            
        file_specs = metadata_payload.get("file_specs", {})
        if not file_specs:
            return candidates
            
        ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="MetadataExtractor",
            parser_version="1.0.0",
            source_element=DocumentElementType.PARAGRAPH
        )
        
        # 1. File Creation
        creation_time = file_specs.get("creation_time")
        if creation_time:
            candidates.append({
                "event_type": TimelineEventType.FILE_CREATED,
                "title": "File Created",
                "description": f"Evidence file was created: {file_path}",
                "raw_timestamp": creation_time,
                "confidence": 1.0,
                "source_reference": ref,
                "location": None,
                "artifacts": [{"evidence_id": evidence_id, "artifact_type": "FILE", "file_name": file_path}]
            })
            
        # 2. File Modification
        mod_time = file_specs.get("modification_time")
        if mod_time:
            candidates.append({
                "event_type": TimelineEventType.FILE_MODIFIED,
                "title": "File Modified",
                "description": f"Evidence file was modified: {file_path}",
                "raw_timestamp": mod_time,
                "confidence": 1.0,
                "source_reference": ref,
                "location": None,
                "artifacts": [{"evidence_id": evidence_id, "artifact_type": "FILE", "file_name": file_path}]
            })
            
        return candidates
export_meta_extractor = MetadataExtractor
