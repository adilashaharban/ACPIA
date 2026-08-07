# -*- coding: utf-8 -*-
"""Metadata metrics generator."""

from typing import Any, Dict, List
from backend.agents.metadata.schema import ExtractionMetrics, MetadataSummary

class MetadataMetricsCalculator:
    """Computes completeness statistics and constructs performance metrics for metadata extraction."""
    
    @staticmethod
    def calculate(
        category: str,
        extractor_name: str,
        details_obj: Any,
        warnings_count: int,
        processing_time_ms: float
    ) -> tuple[ExtractionMetrics, MetadataSummary]:
        """Calculates completeness scores and returns Metrics + Summary contracts.
        
        Args:
            category: File type category (image, audio, etc.).
            extractor_name: Parser class name.
            details_obj: Pydantic sub-schema object (e.g. ImageMetadata).
            warnings_count: Number of validation issues/warnings logged.
            processing_time_ms: Execution duration in milliseconds.
            
        Returns:
            Tuple of (ExtractionMetrics, MetadataSummary).
        """
        fields_extracted = 0
        fields_missing = 0
        completeness = 0.0
        
        has_gps = False
        has_exif = False
        has_camera = False
        has_device = False
        has_doc = False
        
        # Calculate schema fields counts
        if details_obj:
            # Check pydantic model dump
            data_dict = details_obj.model_dump()
            
            # Recurse or inspect flat key/values
            for k, v in data_dict.items():
                if v is not None:
                    fields_extracted += 1
                else:
                    fields_missing += 1
                    
            total_fields = fields_extracted + fields_missing
            completeness = float(fields_extracted) / float(total_fields) if total_fields > 0 else 0.0
            
            # Category flags evaluations
            if category == "image":
                has_exif = True
                if getattr(details_obj, "gps", None) is not None:
                    has_gps = True
                if getattr(details_obj, "camera", None) is not None:
                    has_camera = True
            elif category == "document":
                has_doc = True
        else:
            fields_missing = 5  # default baseline
            
        is_media = category in ("image", "video", "audio")
        
        summary = MetadataSummary(
            file_type_category=category,
            has_gps=has_gps,
            is_media=is_media,
            has_exif=has_exif,
            has_camera=has_camera,
            has_device=has_device,
            has_document_metadata=has_doc,
            metadata_completeness=round(completeness, 4)
        )
        
        metrics = ExtractionMetrics(
            fields_extracted=fields_extracted,
            fields_missing=fields_missing,
            extractor_used=extractor_name,
            warnings_count=warnings_count,
            processing_time_ms=round(processing_time_ms, 2)
        )
        
        return metrics, summary
