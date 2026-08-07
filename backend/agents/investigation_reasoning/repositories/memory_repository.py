# -*- coding: utf-8 -*-
"""In-memory reasoning repository implementation."""

from typing import List, Optional, Dict
from backend.agents.investigation_reasoning.repositories.base_repository import ReasoningRepository
from backend.agents.investigation_reasoning.schema import ReasoningPackage

class MemoryRepository(ReasoningRepository):
    """Stores reasoning packages inside thread-safe local dictionaries."""
    
    def __init__(self) -> None:
        self._packages: Dict[str, ReasoningPackage] = {}

    def save_reasoning(self, package: ReasoningPackage) -> None:
        self._packages[package.reasoning_id] = package

    def load_reasoning(self, reasoning_id: str) -> Optional[ReasoningPackage]:
        return self._packages.get(reasoning_id)

    def list_reasonings(self) -> List[ReasoningPackage]:
        return list(self._packages.values())

    def find_by_case(self, case_id: str) -> List[ReasoningPackage]:
        return [p for p in self.list_reasonings() if p.case_id == case_id]

    def find_by_retrieval(self, retrieval_id: str) -> List[ReasoningPackage]:
        return [p for p in self.list_reasonings() if p.retrieval_id == retrieval_id]

    def find_by_entity(self, entity_id: str) -> List[ReasoningPackage]:
        return [
            p for p in self.list_reasonings()
            if any(entity_id in f.supporting_entities for f in p.findings)
        ]

    def find_by_finding(self, finding_id: str) -> List[ReasoningPackage]:
        return [
            p for p in self.list_reasonings()
            if any(f.finding_id == finding_id for f in p.findings)
        ]

    def delete(self, reasoning_id: str) -> None:
        self._packages.pop(reasoning_id, None)
export_memory_repository = MemoryRepository
