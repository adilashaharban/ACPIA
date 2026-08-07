# -*- coding: utf-8 -*-
"""Communication contracts for the Document Intelligence Agent."""

from backend.agents.base.contracts import RoutingTaskContract
from backend.agents.document_intelligence.schema import DocumentPackage

__all__ = ["DocumentPackage", "RoutingTaskContract"]
