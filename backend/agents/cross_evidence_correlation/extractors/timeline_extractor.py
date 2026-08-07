# -*- coding: utf-8 -*-
"""Timeline observations extractor."""

from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType

class TimelineExtractor:
    """Harvests parsed events from TimelinePackage structures."""
    
    @staticmethod
    def extract(timeline_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateObservation]:
        candidates = []
        if not timeline_payload:
            return candidates
            
        events = timeline_payload.get("events", [])
        for ev in events:
            ev_id = ev.get("event_id")
            title = ev.get("title")
            raw_ts = ev.get("original_timestamp")
            norm_ts_str = ev.get("normalized_timestamp_utc")
            confidence = ev.get("confidence", 0.90)
            
            # Retrieve time object
            from datetime import datetime
            import dateutil.parser
            try:
                dt = dateutil.parser.parse(norm_ts_str)
            except:
                dt = None
                
            refs = ev.get("source_references", [])
            if refs:
                ref = SourceReference.model_validate(refs[0])
            else:
                ref = SourceReference(
                    evidence_id=evidence_id,
                    file_path=file_path,
                    page_number=1,
                    parser="TimelineExtractor",
                    parser_version="1.0.0",
                    source_element=DocumentElementType.PARAGRAPH
                )
                
            candidates.append(
                CandidateObservation(
                    candidate_id=f"CD-TL-TMP-{ev_id}",
                    observation_type=CorrelationType.TEMPORAL_MATCH,
                    originating_agent="timeline_intelligence_agent",
                    evidence_id=evidence_id,
                    raw_value=raw_ts,
                    normalized_value=norm_ts_str,
                    confidence=confidence,
                    timestamp=dt,
                    timeline_event_id=ev_id,
                    source_reference=ref
                )
            )
            
            # Check for geographic location values
            loc = ev.get("location")
            if loc and loc.get("latitude") is not None and loc.get("longitude") is not None:
                lat = float(loc["latitude"])
                lon = float(loc["longitude"])
                addr = loc.get("address")
                
                candidates.append(
                    CandidateObservation(
                        candidate_id=f"CD-TL-LOC-{ev_id}",
                        observation_type=CorrelationType.LOCATION_MATCH,
                        originating_agent="timeline_intelligence_agent",
                        evidence_id=evidence_id,
                        raw_value=addr or f"{lat},{lon}",
                        normalized_value=f"{lat},{lon}",
                        confidence=loc.get("confidence", confidence),
                        latitude=lat,
                        longitude=lon,
                        timeline_event_id=ev_id,
                        source_reference=ref
                    )
                )
                
        return candidates
export_timeline_extractor = TimelineExtractor
