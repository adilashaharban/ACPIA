# -*- coding: utf-8 -*-
"""Evidence registry service managing database interactions and Chain of Custody logs."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.database.models.evidence import Evidence
from backend.database.models.chain_of_custody import ChainOfCustody
from backend.database.repositories.evidence_repository import EvidenceRepository
from backend.agents.evidence_intake.exceptions import DuplicateEvidenceError, DatabaseTransactionError
from backend.schemas.common import ProcessingState

class EvidenceRegistry:
    """Orchestrates evidence metadata registration and audit trails."""
    
    def __init__(self, db: Session) -> None:
        """Initializes the registry with a database session.
        
        Args:
            db: Active SQLAlchemy database session.
        """
        self.repo = EvidenceRepository(db)

    def check_duplicate(self, sha256_hash: str) -> None:
        """Checks if a file with the same SHA-256 hash has already been registered.
        
        Args:
            sha256_hash: File hash checksum.
            
        Raises:
            DuplicateEvidenceError: If the hash is already in the database.
        """
        existing = self.repo.get_by_hash(sha256_hash)
        if existing:
            raise DuplicateEvidenceError(
                f"Evidence with hash {sha256_hash} already registered under case {existing.case_id}.",
                details={
                    "evidence_id": existing.evidence_id,
                    "case_id": existing.case_id,
                    "sha256_hash": sha256_hash,
                }
            )

    def register_evidence(
        self,
        case_id: str,
        uploader: str,
        file_path: str,
        object_storage_path: str,
        sha256_hash: str,
        mime_type: str,
        routing_hints: Optional[List[Dict[str, Any]]] = None
    ) -> Evidence:
        """Registers the evidence metadata record and sets lifecycle status to REGISTERED.
        
        Args:
            case_id: Investigation Case ID.
            uploader: User performing ingestion.
            file_path: Physical local path.
            object_storage_path: Storage URL/URI.
            sha256_hash: SHA-256 hash.
            mime_type: Detected MIME type.
            routing_hints: Suggested downstream agents.
            
        Returns:
            The created Evidence SQLAlchemy database model instance.
            
        Raises:
            DatabaseTransactionError: For SQL write issues.
        """
        # Ensure duplicate check is safe before inserting
        self.check_duplicate(sha256_hash)
        
        evidence_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        db_evidence = Evidence(
            evidence_id=evidence_id,
            case_id=case_id,
            uploader=uploader,
            file_path=file_path,
            object_storage_path=object_storage_path,
            sha256_hash=sha256_hash,
            mime_type=mime_type,
            upload_timestamp=now,
            validation_status=ProcessingState.REGISTERED.value,
            processing_status="READY",
            routing_hints=routing_hints or [],
            integrity_info={
                "verification_method": "SHA-256",
                "verified_at": now.isoformat(),
                "status": "PASS"
            }
        )
        
        try:
            # Create evidence record
            created = self.repo.create(db_evidence)
            
            # Create the initial Chain of Custody entry
            custody_entry = ChainOfCustody(
                entry_id=str(uuid.uuid4()),
                evidence_id=evidence_id,
                timestamp=now,
                action="INGESTED",
                performed_by=uploader,
                description=f"Evidence file successfully ingested, validated, and registered in local storage."
            )
            self.repo.add_custody_entry(custody_entry)
            
            return created
        except Exception as e:
            raise DatabaseTransactionError(f"Database transaction failed during registration: {e}")

    def add_custody_log(
        self,
        evidence_id: str,
        action: str,
        performed_by: str,
        description: str
    ) -> ChainOfCustody:
        """Appends a new event audit entry to the evidence custody log.
        
        Args:
            evidence_id: ID of the evidence.
            action: Action label (e.g. "TRANSFERRED", "PROCESSED").
            performed_by: Identity of uploader or agent module.
            description: Narrative detail of step.
            
        Returns:
            The created ChainOfCustody SQLAlchemy database model instance.
        """
        custody_entry = ChainOfCustody(
            entry_id=str(uuid.uuid4()),
            evidence_id=evidence_id,
            timestamp=datetime.now(timezone.utc),
            action=action,
            performed_by=performed_by,
            description=description
        )
        try:
            return self.repo.add_custody_entry(custody_entry)
        except Exception as e:
            raise DatabaseTransactionError(f"Failed to append custody log entry: {e}")
            
    def get_custody_trail(self, evidence_id: str) -> List[ChainOfCustody]:
        """Retrieves history audit trail of custody records for the given evidence.
        
        Args:
            evidence_id: Target evidence ID.
            
        Returns:
            A list of ChainOfCustody database model instances.
        """
        return self.repo.get_custody_log(evidence_id)
