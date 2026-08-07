# -*- coding: utf-8 -*-
"""Evidence Intake processing pipeline."""

import time
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from backend.core.logger import get_logger
from backend.schemas.evidence import EvidenceMetadata
from backend.agents.base.contracts import EvidencePackageContract, RoutingTaskContract
from backend.agents.evidence_intake.constants import IntakeState
from backend.agents.evidence_intake.validator import EvidenceValidator
from backend.agents.evidence_intake.hashing import EvidenceHasher
from backend.agents.evidence_intake.storage import LocalStorageProvider
from backend.agents.evidence_intake.registry import EvidenceRegistry
from backend.agents.evidence_intake.router import EvidenceRouter
from backend.schemas.common import ProcessingState

logger = get_logger("agents.evidence_intake.pipeline")


class EvidenceIntakePipeline:
    """Executes the sequential, deterministic workflow stages of evidence ingestion."""
    
    def __init__(self, db: Session) -> None:
        """Initializes pipeline with DB session and defaults.
        
        Args:
            db: SQLAlchemy session.
        """
        self.db = db
        self.storage = LocalStorageProvider()
        self.registry = EvidenceRegistry(db)

    def execute(
        self, 
        file_bytes: bytes, 
        filename: str, 
        case_id: str, 
        uploader: str
    ) -> Tuple[EvidencePackageContract, List[str]]:
        """Executes the ingestion pipeline.
        
        Args:
            file_bytes: Uploaded binary content.
            filename: User-provided original filename.
            case_id: Active Case ID.
            uploader: Name of user.
            
        Returns:
            Tuple containing the final EvidencePackageContract and warnings list.
        """
        warnings: List[str] = []
        logger.info(
            "Evidence ingestion execution started.", 
            extra={"extra_attrs": {"case_id": case_id, "filename": filename, "uploader": uploader}}
        )
        
        # 1. Validation
        logger.info("Executing file validations...")
        sanitized_name, mime_type = EvidenceValidator.validate(file_bytes, filename)
        logger.info(
            f"File validation passed. Sanitized name: {sanitized_name}, MIME type: {mime_type}"
        )
        
        # 2. Hash computation
        logger.info("Computing SHA-256 integrity signature...")
        sha256_hash = EvidenceHasher.compute_hash(file_bytes)
        logger.info(f"SHA-256 computed: {sha256_hash}")
        
        # 3. Duplicate detection
        logger.info("Checking for duplicate evidence records...")
        self.registry.check_duplicate(sha256_hash)
        
        # 4. Storage persistence
        logger.info("Persisting binary to storage layer...")
        file_path, object_storage_path = self.storage.store(
            file_bytes=file_bytes,
            case_id=case_id,
            filename=sanitized_name,
            sha256_hash=sha256_hash
        )
        logger.info(f"File stored. Path: {file_path}")
        
        # 5. Router instructions
        logger.info("Computing routing instructions based on file signature...")
        routing_tasks = EvidenceRouter.get_routing_tasks(mime_type)
        logger.info(f"Routing targets resolved: {[task.agent for task in routing_tasks]}")
        
        # 6. Database metadata registration
        logger.info("Writing registration record and Chain of Custody...")
        db_evidence = self.registry.register_evidence(
            case_id=case_id,
            uploader=uploader,
            file_path=file_path,
            object_storage_path=object_storage_path,
            sha256_hash=sha256_hash,
            mime_type=mime_type,
            routing_hints=[task.model_dump() for task in routing_tasks]
        )
        
        # 7. Package creation
        custody_records = self.registry.get_custody_trail(db_evidence.evidence_id)
        custody_trail = [
            {
                "entry_id": c.entry_id,
                "evidence_id": c.evidence_id,
                "timestamp": c.timestamp.isoformat(),
                "action": c.action,
                "performed_by": c.performed_by,
                "description": c.description,
            }
            for c in custody_records
        ]
        
        evidence_meta = EvidenceMetadata(
            evidence_id=db_evidence.evidence_id,
            case_id=db_evidence.case_id,
            uploader=db_evidence.uploader,
            file_path=db_evidence.file_path,
            object_storage_path=db_evidence.object_storage_path,
            sha256_hash=db_evidence.sha256_hash,
            mime_type=db_evidence.mime_type,
            upload_timestamp=db_evidence.upload_timestamp,
            validation_status=ProcessingState.READY,
            processing_status="READY",
            routing_hints=db_evidence.routing_hints,
            integrity_info=db_evidence.integrity_info
        )
        
        package = EvidencePackageContract(
            schema_version="1.0.0",
            agent_version="1.0.0",
            pipeline_version="1.0.0",
            evidence_metadata=evidence_meta,
            chain_of_custody_log=custody_trail,
            next_agents=routing_tasks
        )
        
        logger.info("Ingestion pipeline successfully completed.")
        return package, warnings
