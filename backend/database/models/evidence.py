# -*- coding: utf-8 -*-
"""Evidence database model definition."""

import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON
from sqlalchemy.orm import relationship
from backend.database.base import Base

class Evidence(Base):
    """SQLAlchemy model representing ingested evidence files."""
    
    __tablename__ = "evidence"
    
    evidence_id = Column(String(36), primary_key=True, index=True)
    case_id = Column(String(100), nullable=False, index=True)
    uploader = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    object_storage_path = Column(String(500), nullable=False)
    sha256_hash = Column(String(64), nullable=False, unique=True, index=True)
    mime_type = Column(String(100), nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    validation_status = Column(String(50), nullable=False)  # RECEIVED, VALIDATED, etc.
    processing_status = Column(String(50), nullable=False)  # READY, PROCESSING, etc.
    routing_hints = Column(JSON, nullable=True)  # Downstream destinations list
    integrity_info = Column(JSON, nullable=True)  # Hash validation metadata
    
    # Relationships
    chain_of_custody = relationship(
        "ChainOfCustody", 
        back_populates="evidence", 
        cascade="all, delete-orphan"
    )
