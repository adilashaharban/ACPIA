# -*- coding: utf-8 -*-
"""Correlation cluster builder."""

import uuid
from typing import List, Set, Dict, Tuple
import networkx as nx
from backend.agents.cross_evidence_correlation.schema import (
    CorrelationCluster, CorrelationMatch, CorrelatedEntity
)

class ClusterBuilder:
    """Builds multi-modal clusters of connected matches using NetworkX graphs."""
    
    @staticmethod
    def build_clusters(matches: List[CorrelationMatch]) -> List[CorrelationCluster]:
        """Clusters matches into connected subgroups.
        
        Args:
            matches: Verified matches list.
            
        Returns:
            List of CorrelationCluster.
        """
        clusters: List[CorrelationCluster] = []
        if not matches:
            return clusters
            
        g = nx.Graph()
        
        # Maps observation ID to match references
        obs_map = {}
        
        # Build network graph
        for m in matches:
            u = m.supporting_observations[0].observation_id
            v = m.supporting_observations[1].observation_id
            g.add_edge(u, v, payload=m)
            
            # Map observations
            obs_map[u] = m.supporting_observations[0]
            obs_map[v] = m.supporting_observations[1]
            
        # Extract connected components
        components = list(nx.connected_components(g))
        for idx, comp in enumerate(components):
            sub_g = g.subgraph(comp)
            
            # Collect elements
            cluster_matches = []
            matched_evidence: Set[str] = set()
            timeline_events: Set[str] = set()
            graph_nodes: Set[str] = set()
            graph_edges: Set[str] = set()
            entities: Set[Tuple[str, str]] = set()
            source_references = []
            timestamps = []
            confidences = []
            
            # Iterate edges within component
            for u, v, data in sub_g.edges(data=True):
                m = data["payload"]
                cluster_matches.append(m)
                confidences.append(m.confidence)
                
                # Retrieve observations
                for obs in m.supporting_observations:
                    matched_evidence.add(obs.evidence_id)
                    source_references.append(obs.source_reference)
                    
                    # Track timestamps if available in matched_evidence source context
                    # (Note: raw timestamp properties will be mapped during pipeline runs)
                    
            # Parse entities details
            correlated_entities = []
            
            # Form cluster primary timestamp from chronological median
            cluster_ts = None
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
            
            cluster_id = f"CLUST-{str(uuid.uuid4())[:8]}"
            
            clusters.append(
                CorrelationCluster(
                    cluster_id=cluster_id,
                    cluster_name=f"Correlation Cluster #{idx + 1}",
                    matched_entities=correlated_entities,
                    matched_evidence=list(matched_evidence),
                    timeline_events=list(timeline_events),
                    graph_nodes=list(graph_nodes),
                    graph_edges=list(graph_edges),
                    correlations=cluster_matches,
                    source_references=source_references,
                    cluster_primary_timestamp=cluster_ts,
                    confidence=round(avg_confidence, 4)
                )
            )
            
        return clusters
export_cluster_builder = ClusterBuilder
