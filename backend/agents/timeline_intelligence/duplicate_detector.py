# -*- coding: utf-8 -*-
"""Timeline duplicates detector."""

from typing import List
from backend.agents.timeline_intelligence.schema import TimelineEvent
from backend.agents.timeline_intelligence.constants import DUPLICATE_PROXIMITY_SECONDS

class DuplicateDetector:
    """Groups duplicate timeline events occurring in close temporal proximity."""
    
    @staticmethod
    def detect_groups(events: List[TimelineEvent]) -> List[List[TimelineEvent]]:
        """Groups events of the same type occurring within proximity bounds.
        
        Args:
            events: List of TimelineEvent.
            
        Returns:
            List of TimelineEvent clusters.
        """
        sorted_events = sorted(events, key=lambda x: (x.event_type.name, x.normalized_timestamp_utc))
        groups: List[List[TimelineEvent]] = []
        
        if not sorted_events:
            return groups
            
        current_group = [sorted_events[0]]
        for event in sorted_events[1:]:
            last_event = current_group[-1]
            
            # Check type matching and timestamp proximity
            time_diff = abs((event.normalized_timestamp_utc - last_event.normalized_timestamp_utc).total_seconds())
            if event.event_type == last_event.event_type and time_diff <= DUPLICATE_PROXIMITY_SECONDS:
                current_group.append(event)
            else:
                groups.append(current_group)
                current_group = [event]
                
        if current_group:
            groups.append(current_group)
            
        return groups
export_duplicate_detector = DuplicateDetector
