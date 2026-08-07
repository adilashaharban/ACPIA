# -*- coding: utf-8 -*-
"""Routing engine assigning downstream analysis tasks based on MIME classifications."""

from typing import List
from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.evidence_intake.constants import MIME_GROUPS, DEFAULT_PRIORITIES

class EvidenceRouter:
    """Decides downstream investigation agent pipelines using MIME-type mapping rules."""
    
    @staticmethod
    def get_routing_tasks(mime_type: str) -> List[RoutingTaskContract]:
        """Maps mime type classification to structured downstream routing tasks.
        
        Args:
            mime_type: Verified file content MIME string.
            
        Returns:
            List of RoutingTaskContract tasks to guide orchestration.
        """
        tasks: List[RoutingTaskContract] = []
        
        # Metadata is universally required for processing and indexing
        tasks.append(
            RoutingTaskContract(
                agent="metadata",
                priority=DEFAULT_PRIORITIES.get("metadata", 1)
            )
        )
        
        # Route specific types to matching core agents
        if mime_type in MIME_GROUPS["image"]:
            tasks.append(
                RoutingTaskContract(
                    agent="vision",
                    priority=DEFAULT_PRIORITIES.get("vision", 2)
                )
            )
            
        elif mime_type in MIME_GROUPS["pdf"] or mime_type in MIME_GROUPS["text"]:
            tasks.append(
                RoutingTaskContract(
                    agent="document",
                    priority=DEFAULT_PRIORITIES.get("document", 2)
                )
            )
            
        elif mime_type in MIME_GROUPS["audio"]:
            tasks.append(
                RoutingTaskContract(
                    agent="audio",
                    priority=DEFAULT_PRIORITIES.get("audio", 2)
                )
            )
            
        elif mime_type in MIME_GROUPS["video"]:
            # Videos get routed to both Vision and Audio analysis pipelines
            tasks.append(
                RoutingTaskContract(
                    agent="vision",
                    priority=DEFAULT_PRIORITIES.get("vision", 2)
                )
            )
            tasks.append(
                RoutingTaskContract(
                    agent="audio",
                    priority=DEFAULT_PRIORITIES.get("audio", 2)
                )
            )
            
        elif mime_type in MIME_GROUPS["archive"]:
            # Archives are registered and their content can be processed as sub-elements later
            tasks.append(
                RoutingTaskContract(
                    agent="archive_extractor",
                    priority=2
                )
            )
            
        return tasks
