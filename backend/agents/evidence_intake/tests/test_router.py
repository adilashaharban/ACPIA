# -*- coding: utf-8 -*-
"""Unit tests for routing logic."""

from backend.agents.evidence_intake.router import EvidenceRouter

def test_router_image_routing() -> None:
    """Verifies that an image maps to Vision and Metadata agents."""
    tasks = EvidenceRouter.get_routing_tasks("image/png")
    agents = [t.agent for t in tasks]
    assert "metadata" in agents
    assert "vision" in agents
    assert "document" not in agents

def test_router_document_routing() -> None:
    """Verifies that a PDF maps to Document and Metadata agents."""
    tasks = EvidenceRouter.get_routing_tasks("application/pdf")
    agents = [t.agent for t in tasks]
    assert "metadata" in agents
    assert "document" in agents
    assert "vision" not in agents

def test_router_video_routing() -> None:
    """Verifies that a video maps to Vision, Audio, and Metadata agents."""
    tasks = EvidenceRouter.get_routing_tasks("video/mp4")
    agents = [t.agent for t in tasks]
    assert "metadata" in agents
    assert "vision" in agents
    assert "audio" in agents
