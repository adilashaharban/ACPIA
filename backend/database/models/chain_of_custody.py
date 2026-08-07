# -*- coding: utf-8 -*-
"""Chain of Custody database model definition."""

import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.base import Base

class ChainOfCustody(Base):
    """SQLAlchemy model tracking custody audit trails."""
    
    __tablename__ = "chain_of_custody"
    
    entry_id = Column(String(36), primary_key=True, index=True)
    evidence_id = Column(String(36), ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    action = Column(String(100), nullable=False)  # INGESTED, VERIFIED, TRANSFERRED
    performed_by = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Relationships
    evidence = relationship("Evidence", back_populates="chain_of_custody")
