# -*- coding: utf-8 -*-
"""Abstract base class definition for all ACPIA agents."""

from abc import ABC, abstractmethod
from backend.agents.base.agent_result import AgentResultContract
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.base.manifest import AgentManifest

class BaseAgent(ABC):
    """Unified agent contract providing uniform execution and discovery APIs."""
    
    @abstractmethod
    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Executes the agent's core pipeline task.
        
        Args:
            context: Active tracing context block.
            **kwargs: Step-specific parameters.
            
        Returns:
            Standard AgentResultContract wrapping results and metrics.
        """
        pass

    @abstractmethod
    def health(self) -> dict:
        """Reports the health and dependency connectivity status of this agent.
        
        Returns:
            A dictionary containing health details.
        """
        pass

    @abstractmethod
    def manifest(self) -> AgentManifest:
        """Exposes capability registration schemas and descriptions.
        
        Returns:
            A populated AgentManifest description object.
        """
        pass
