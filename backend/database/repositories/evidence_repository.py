# -*- coding: utf-8 -*-
"""Evidence repository implementing data access patterns."""

from typing import Optional, List
from sqlalchemy.orm import Session
from backend.database.models.evidence import Evidence
from backend.database.models.chain_of_custody import ChainOfCustody

class EvidenceRepository:
    """Repository managing database persistence for evidence files."""
    
    def __init__(self, db: Session) -> None:
        """Initializes the repository with a database session.
        
        Args:
            db: Active SQLAlchemy database session.
        """
        self.db = db

    def get_by_id(self, evidence_id: str) -> Optional[Evidence]:
        """Retrieves evidence record by its primary ID.
        
        Args:
            evidence_id: Unique UUID of the evidence.
            
        Returns:
            The Evidence instance if found, else None.
        """
        return self.db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()

    def get_by_hash(self, sha256_hash: str) -> Optional[Evidence]:
        """Retrieves evidence record by its SHA-256 hash.
        
        Args:
            sha256_hash: Hashed signature of the file.
            
        Returns:
            The Evidence instance if found, else None.
        """
        return self.db.query(Evidence).filter(Evidence.sha256_hash == sha256_hash).first()

    def create(self, evidence: Evidence) -> Evidence:
        """Saves a new evidence record.
        
        Args:
            evidence: Populate Evidence database model.
            
        Returns:
            The persisted Evidence instance.
        """
        self.db.add(evidence)
        self.db.flush()
        return evidence

    def add_custody_entry(self, entry: ChainOfCustody) -> ChainOfCustody:
        """Appends a new entry to the chain of custody log.
        
        Args:
            entry: Populated ChainOfCustody database model.
            
        Returns:
            The persisted ChainOfCustody entry.
        """
        self.db.add(entry)
        self.db.flush()
        return entry

    def get_custody_log(self, evidence_id: str) -> List[ChainOfCustody]:
        """Retrieves the history trail of custody logs for an evidence.
        
        Args:
            evidence_id: Target evidence ID.
            
        Returns:
            A list of ChainOfCustody objects.
        """
        return (
            self.db.query(ChainOfCustody)
            .filter(ChainOfCustody.evidence_id == evidence_id)
            .order_by(ChainOfCustody.timestamp.asc())
            .all()
        )
