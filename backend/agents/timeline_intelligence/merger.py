# -*- coding: utf-8 -*-
"""Timeline event merge logic."""

from typing import List, Set
from backend.agents.timeline_intelligence.schema import TimelineEvent

class EventMerger:
    """Merges clusters of duplicate events into a single normalized entry."""
    
    @staticmethod
    def merge_events(cluster: List[TimelineEvent]) -> TimelineEvent:
        """Consolidates duplicate events by merging reference lists.
        
        Args:
            cluster: Cluster of events.
            
        Returns:
            A single merged TimelineEvent object.
        """
        if not cluster:
            raise ValueError("Merge cluster cannot be empty.")
            
        # Prioritize highest confidence
        sorted_cluster = sorted(cluster, key=lambda x: x.confidence, reverse=True)
        primary = sorted_cluster[0]
        
        # Merge properties
        artifacts = []
        entities: Set[str] = set()
        graph_nodes: Set[str] = set()
        graph_edges: Set[str] = set()
        source_references = []
        observations = []
        
        for event in cluster:
            artifacts.extend(event.artifacts)
            entities.update(event.entities)
            graph_nodes.update(event.graph_nodes)
            graph_edges.update(event.graph_edges)
            source_references.extend(event.source_references)
            observations.extend(event.supporting_observations)
            
        # Build merged object
        return TimelineEvent(
            event_id=primary.event_id,
            event_type=primary.event_type,
            title=primary.title,
            description=primary.description,
            temporal_range=primary.temporal_range,
            original_timestamp=primary.original_timestamp,
            normalized_timestamp_utc=primary.normalized_timestamp_utc,
            timestamp_precision=primary.timestamp_precision,
            timezone=primary.timezone,
            timestamp_confidence=primary.timestamp_confidence,
            origin=primary.origin,
            sequence_number=0,  # assigned by sorter
            location=primary.location,
            artifacts=artifacts,
            entities=list(entities),
            graph_nodes=list(graph_nodes),
            graph_edges=list(graph_edges),
            source_references=source_references,
            supporting_observations=observations,
            confidence=round(sum(e.confidence for e in cluster)/len(cluster), 4)
        )
export_merger = EventMerger
