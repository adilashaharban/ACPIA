# -*- coding: utf-8 -*-
"""Timeline chronological sorter module."""

from typing import List, Tuple, Dict
from backend.agents.timeline_intelligence.schema import TimelineEvent

class ChronologicalSorter:
    """Sorts timeline events chronologically and assigns stable sequence numbers."""
    
    @staticmethod
    def sort_and_index(events: List[TimelineEvent]) -> Tuple[List[TimelineEvent], Dict[str, int]]:
        """Sorts events and maps indexes.
        
        Args:
            events: List of TimelineEvent.
            
        Returns:
            Tuple containing sorted TimelineEvents and event index dictionary.
        """
        sorted_events = sorted(events, key=lambda x: x.normalized_timestamp_utc)
        event_index: Dict[str, int] = {}
        
        for idx, event in enumerate(sorted_events):
            event.sequence_number = idx + 1
            event_index[event.event_id] = event.sequence_number
            
        return sorted_events, event_index
export_sorter = ChronologicalSorter
