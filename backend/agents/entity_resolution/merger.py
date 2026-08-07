# -*- coding: utf-8 -*-
"""Entity merge module."""

import uuid
from typing import List, Set
from backend.agents.entity_resolution.schema import (
    CanonicalEntity, CandidateEntity, EntityObservation, EntityAlias, EntityAttribute,
    ResolutionMethod, ConfidenceBreakdown, MatchingEvidence
)

class EntityMerger:
    """Merges matching CandidateEntity structures into deduplicated CanonicalEntity references."""
    
    @staticmethod
    def merge_cluster(
        cluster: List[CandidateEntity], 
        matches: List[MatchingEvidence],
        confidence_breakdown: ConfidenceBreakdown
    ) -> CanonicalEntity:
        """Consolidates matched candidates into a single CanonicalEntity.
        
        Args:
            cluster: List of CandidateEntity records belonging to the same cluster.
            matches: MatchingEvidence references linking them.
            confidence_breakdown: Confidence breakdown parameters.
            
        Returns:
            A CanonicalEntity object.
        """
        # 1. Resolve canonical name (highest confidence wins)
        sorted_cluster = sorted(cluster, key=lambda x: x.confidence, reverse=True)
        primary = sorted_cluster[0]
        canonical_name = primary.normalized_value
        
        # 2. Gather aliases and attributes
        aliases: List[EntityAlias] = []
        attributes: List[EntityAttribute] = []
        observations: List[EntityObservation] = []
        linked_evidence: Set[str] = set()
        source_references = []
        
        for cand in cluster:
            linked_evidence.add(cand.source_reference.evidence_id)
            source_references.append(cand.source_reference)
            
            # Supporting observation
            observations.append(
                EntityObservation(
                    observation_id=cand.candidate_id,
                    evidence_id=cand.source_reference.evidence_id,
                    entity_type=cand.entity_type,
                    raw_value=cand.raw_value,
                    normalized_value=cand.normalized_value,
                    confidence=cand.confidence,
                    source_reference=cand.source_reference
                )
            )
            
            # If name differs, register as alias
            if cand.normalized_value != canonical_name:
                aliases.append(
                    EntityAlias(
                        alias_name=cand.raw_value,
                        confidence=cand.confidence,
                        source_reference=cand.source_reference
                    )
                )
                
            # Attributes
            for attr in cand.supporting_attributes:
                attributes.append(attr)
                
        # Resolve creation method based on matches
        creation_method = ResolutionMethod.EXACT_MATCH
        for m in matches:
            if m.algorithm.name in ["JARO_WINKLER", "LEVENSHTEIN"]:
                creation_method = ResolutionMethod.FUZZY_MATCH
                break
                
        return CanonicalEntity(
            entity_id=f"ENT-{primary.entity_type.name[:3]}-{primary.candidate_id[:8]}",
            entity_type=primary.entity_type,
            canonical_name=canonical_name,
            aliases=aliases,
            attributes=attributes,
            confidence_breakdown=confidence_breakdown,
            source_references=source_references,
            supporting_observations=observations,
            linked_evidence=list(linked_evidence),
            creation_method=creation_method
        )
