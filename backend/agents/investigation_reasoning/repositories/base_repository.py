# -*- coding: utf-8 -*-
"""Reasoning repository base interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from backend.agents.investigation_reasoning.schema import ReasoningPackage

class ReasoningRepository(ABC):
    """Abstract interface for storing and loading reasoning packages."""
    
    @abstractmethod
    def save_reasoning(self, package: ReasoningPackage) -> None:
        """Stores a reasoning package."""
        pass

    @abstractmethod
    def load_reasoning(self, reasoning_id: str) -> Optional[ReasoningPackage]:
        """Loads a reasoning package by ID."""
        pass

    @abstractmethod
    def list_reasonings(self) -> List[ReasoningPackage]:
        """Lists all stored packages."""
        pass

    @abstractmethod
    def find_by_case(self, case_id: str) -> List[ReasoningPackage]:
        """Filters by case ID."""
        pass

    @abstractmethod
    def find_by_retrieval(self, retrieval_id: str) -> List[ReasoningPackage]:
        """Filters by retrieval search reference ID."""
        pass

    @abstractmethod
    def find_by_entity(self, entity_id: str) -> List[ReasoningPackage]:
        """Filters by associated canonical entity ID."""
        pass

    @abstractmethod
    def find_by_finding(self, finding_id: str) -> List[ReasoningPackage]:
        """Filters by specific finding ID reference."""
        pass

    @abstractmethod
    def delete(self, reasoning_id: str) -> None:
        """Removes a package by ID."""
        pass
export_base_repository = ReasoningRepository
