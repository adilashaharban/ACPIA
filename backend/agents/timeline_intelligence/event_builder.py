# -*- coding: utf-8 -*-
"""TimelineEvent builder module."""

import uuid
from datetime import datetime
from typing import Dict, Any
from backend.agents.timeline_intelligence.schema import (
    TimelineEvent, TemporalRange, EventSource, EventLocation, EventArtifact, TimelineObservation, TimestampPrecision
)

class EventBuilder:
    """Transforms raw candidate event metrics into TimelineEvent schemas."""
    
    @staticmethod
    def build_event(
        cand: Dict[str, Any], 
        processing_id: str, 
        normalized_time: datetime,
        precision: TimestampPrecision
    ) -> TimelineEvent:
        """Assembles standard Pydantic timeline elements.
        
        Args:
            cand: Candidate information dictionary.
            processing_id: Active tracing process ID.
            normalized_time: Normalized UTC datetime.
            precision: Precision level enum.
            
        Returns:
            TimelineEvent object.
        """
        event_id = f"EVT-{cand['event_type'].name[:3]}-{str(uuid.uuid4())[:8]}"
        ref = cand["source_reference"]
        
        # Build EventSource block
        origin = EventSource(
            agent_name="timeline_intelligence",
            package_version="1.0.0",
            processing_id=processing_id,
            evidence_id=ref.evidence_id,
            source_reference=ref
        )
        
        # Build TemporalRange
        temporal_range = TemporalRange(
            start_time=normalized_time,
            end_time=None,
            duration_seconds=None
        )
        
        # Location mapping
        location = None
        loc_dict = cand.get("location")
        if loc_dict:
            location = EventLocation(
                latitude=loc_dict.get("latitude"),
                longitude=loc_dict.get("longitude"),
                address=loc_dict.get("address"),
                confidence=loc_dict.get("confidence", 1.0),
                source_reference=ref
            )
            
        # Artifacts mapping
        artifacts = []
        for art in cand.get("artifacts") or []:
            artifacts.append(
                EventArtifact(
                    evidence_id=art["evidence_id"],
                    artifact_type=art["artifact_type"],
                    file_name=art["file_name"],
                    source_reference=ref
                )
            )
            
        # Supporting Observation mapping
        obs_id = f"OBS-{str(uuid.uuid4())[:8]}"
        observations = [
            TimelineObservation(
                observation_id=obs_id,
                evidence_id=ref.evidence_id,
                raw_value=cand["raw_timestamp"],
                confidence=cand["confidence"],
                source_reference=ref
            )
        ]
        
        return TimelineEvent(
            event_id=event_id,
            event_type=cand["event_type"],
            title=cand["title"],
            description=cand["description"],
            temporal_range=temporal_range,
            original_timestamp=cand["raw_timestamp"],
            normalized_timestamp_utc=normalized_time,
            timestamp_precision=precision,
            timestamp_confidence=cand["confidence"],
            origin=origin,
            sequence_number=0,  # assigned by sorter
            location=location,
            artifacts=artifacts,
            entities=cand.get("entities") or [],
            graph_nodes=cand.get("graph_nodes") or [],
            graph_edges=cand.get("graph_edges") or [],
            source_references=[ref],
            supporting_observations=observations,
            confidence=cand["confidence"]
        )
export_event_builder = EventBuilder
