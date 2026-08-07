# -*- coding: utf-8 -*-
"""Graph observations extractor."""

import dateutil.parser
from typing import List, Dict, Any
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.cross_evidence_correlation.schema import CandidateObservation, CorrelationType

class GraphExtractor:
    """Harvests observed node entities and attributes from the Knowledge Graph."""
    
    @staticmethod
    def extract(graph_payload: Dict[str, Any], file_path: str, evidence_id: str) -> List[CandidateObservation]:
        candidates = []
        if not graph_payload:
            return candidates
            
        nodes = graph_payload.get("nodes", [])
        for node in nodes:
            node_id = node.get("node_id")
            node_type = node.get("node_type")
            properties = node.get("properties", [])
            
            # Map location node coordinate candidates
            if node_type == "LOCATION":
                lat = None
                lon = None
                addr = None
                confidence = node.get("confidence", 0.90)
                
                # Exclude node details if no properties exist
                for prop in properties:
                    k = prop.get("key")
                    v = prop.get("value")
                    if k == "latitude" and v:
                        lat = float(v)
                    elif k == "longitude" and v:
                        lon = float(v)
                    elif k == "address" and v:
                        addr = str(v)
                        
                if lat is not None and lon is not None:
                    # Find reference
                    ref = None
                    if properties:
                        ref_dict = properties[0].get("source_reference")
                        if ref_dict:
                            ref = SourceReference.model_validate(ref_dict)
                            
                    if not ref:
                        ref = SourceReference(
                            evidence_id=evidence_id,
                            file_path=file_path,
                            page_number=1,
                            parser="GraphExtractor",
                            parser_version="1.0.0",
                            source_element=DocumentElementType.PARAGRAPH
                        )
                        
                    candidates.append(
                        CandidateObservation(
                            candidate_id=f"CD-GR-LOC-{node_id}",
                            observation_type=CorrelationType.LOCATION_MATCH,
                            originating_agent="knowledge_graph_agent",
                            evidence_id=evidence_id,
                            raw_value=addr or f"{lat},{lon}",
                            normalized_value=f"{lat},{lon}",
                            confidence=confidence,
                            latitude=lat,
                            longitude=lon,
                            graph_node_id=node_id,
                            source_reference=ref
                        )
                    )
                    
            # Map node attributes
            for prop in properties:
                key = prop.get("key")
                val = prop.get("value")
                
                if key in ["timestamp", "created_at", "occurred_at"] and val:
                    try:
                        dt = dateutil.parser.parse(str(val))
                    except:
                        dt = None
                        
                    ref_dict = prop.get("source_reference")
                    if ref_dict:
                        ref = SourceReference.model_validate(ref_dict)
                    else:
                        ref = SourceReference(
                            evidence_id=evidence_id,
                            file_path=file_path,
                            page_number=1,
                            parser="GraphExtractor",
                            parser_version="1.0.0",
                            source_element=DocumentElementType.PARAGRAPH
                        )
                        
                    candidates.append(
                        CandidateObservation(
                            candidate_id=f"CD-GR-TMP-{node_id}",
                            observation_type=CorrelationType.TEMPORAL_MATCH,
                            originating_agent="knowledge_graph_agent",
                            evidence_id=evidence_id,
                            raw_value=str(val),
                            normalized_value=str(val),
                            confidence=prop.get("confidence", 0.90),
                            timestamp=dt,
                            graph_node_id=node_id,
                            source_reference=ref
                        )
                    )
                    
        return candidates
export_graph_extractor = GraphExtractor
