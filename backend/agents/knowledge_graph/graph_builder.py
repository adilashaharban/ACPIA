# -*- coding: utf-8 -*-
"""Graph builder orchestrator."""

from datetime import datetime, timezone
import uuid
from typing import List, Dict, Tuple
import networkx as nx
from backend.agents.knowledge_graph.schema import (
    GraphNode, GraphEdge, KnowledgeGraphPackage, GraphStatistics, GraphSummary,
    GraphValidation, GraphMetrics, ProcessorExecution
)

class GraphBuilder:
    """Orchestrates node and edge aggregation, duplicates deduplication, and NetworkX stats compilation."""
    
    @staticmethod
    def deduplicate_nodes(nodes: List[GraphNode]) -> List[GraphNode]:
        """Merges duplicate nodes sharing the same node_id or entity_id.
        
        Args:
            nodes: Input node list.
            
        Returns:
            List of merged unique GraphNodes.
        """
        merged: Dict[str, GraphNode] = {}
        for node in nodes:
            key = node.node_id
            if key not in merged:
                merged[key] = node
            else:
                # Merge properties, observations, source references
                existing = merged[key]
                existing.properties.extend(
                    [p for p in node.properties if p.key not in {ep.key for ep in existing.properties}]
                )
                existing.source_references.extend(
                    [r for r in node.source_references if r.evidence_id not in {er.evidence_id for er in existing.source_references}]
                )
                existing.supporting_observations.extend(
                    [o for o in node.supporting_observations if o.observation_id not in {eo.observation_id for eo in existing.supporting_observations}]
                )
                existing.confidence = max(existing.confidence, node.confidence)
                
        return list(merged.values())

    @staticmethod
    def deduplicate_edges(edges: List[GraphEdge]) -> List[GraphEdge]:
        """Merges duplicate edges sharing the same source/target IDs and EdgeType.
        
        Args:
            edges: Input edge list.
            
        Returns:
            List of merged unique GraphEdges.
        """
        merged: Dict[Tuple[str, str, str], GraphEdge] = {}
        for edge in edges:
            key = (edge.source_node_id, edge.target_node_id, edge.edge_type.name)
            if key not in merged:
                merged[key] = edge
            else:
                existing = merged[key]
                existing.supporting_evidence.extend(
                    [r for r in edge.supporting_evidence if r.evidence_id not in {er.evidence_id for er in existing.supporting_evidence}]
                )
                existing.supporting_observations.extend(
                    [o for o in edge.supporting_observations if o.observation_id not in {eo.observation_id for eo in existing.supporting_observations}]
                )
                existing.confidence = max(existing.confidence, edge.confidence)
                
        return list(merged.values())

    @classmethod
    def assemble_package(
        cls,
        case_id: str,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
        validation: GraphValidation,
        metrics: GraphMetrics
    ) -> KnowledgeGraphPackage:
        """Assembles node/edge stats and packages the final KnowledgeGraphPackage.
        
        Args:
            case_id: Active Case ID.
            nodes: Deduplicated nodes.
            edges: Deduplicated edges.
            validation: Integrity checks validation status.
            metrics: Process timings metrics.
            
        Returns:
            KnowledgeGraphPackage object.
        """
        # Deduplicate
        unique_nodes = cls.deduplicate_nodes(nodes)
        unique_edges = cls.deduplicate_edges(edges)
        
        # Calculate stats using NetworkX
        g = nx.MultiDiGraph()
        for node in unique_nodes:
            g.add_node(node.node_id)
        for edge in unique_edges:
            g.add_edge(edge.source_node_id, edge.target_node_id)
            
        isolated_count = len(list(nx.isolates(g)))
        # Convert MultiDiGraph to simple DiGraph to compute standard density
        simple_g = nx.DiGraph(g)
        density = nx.density(simple_g)
        
        statistics = GraphStatistics(
            node_count=len(unique_nodes),
            edge_count=len(unique_edges),
            isolated_node_count=isolated_count,
            density=round(density, 4)
        )
        
        # Categorize node/edge type distributions
        node_dist = {}
        for n in unique_nodes:
            node_dist[n.node_type.name] = node_dist.get(n.node_type.name, 0) + 1
            
        edge_dist = {}
        for e in unique_edges:
            edge_dist[e.edge_type.name] = edge_dist.get(e.edge_type.name, 0) + 1
            
        summary = GraphSummary(
            node_distribution=node_dist,
            edge_distribution=edge_dist
        )
        
        return KnowledgeGraphPackage(
            schema_version="1.0.0",
            graph_id=f"GRPH-{str(uuid.uuid4())[:8]}",
            case_id=case_id,
            created_at=datetime.now(timezone.utc),
            graph_version="1.0.0",
            nodes=unique_nodes,
            edges=unique_edges,
            statistics=statistics,
            validation=validation,
            metrics=metrics,
            summary=summary
        )
export_graph_builder = GraphBuilder
