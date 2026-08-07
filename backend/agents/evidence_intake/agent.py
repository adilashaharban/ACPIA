# -*- coding: utf-8 -*-
"""Evidence Intake Agent implementation."""

import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from backend.core.logger import get_logger
from backend.database.session import get_db_context
from backend.agents.base.base_agent import BaseAgent
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.base.agent_result import AgentResultContract
from backend.agents.base.metadata import AgentMetadata
from backend.agents.base.manifest import AgentManifest
from backend.agents.evidence_intake.pipeline import EvidenceIntakePipeline
from backend.agents.evidence_intake.exceptions import EvidenceIntakeError

logger = get_logger("agents.evidence_intake.agent")


class EvidenceIntakeAgent(BaseAgent):
    """Entry point agent managing secure file onboarding pipelines."""
    
    # Declarative Manifest
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="evidence_intake",
            version="1.0.0",
            description="Secure entrypoint agent verifying, hashing, storing, and registering incoming evidence.",
            supported_input_types=["multipart/form-data", "binary"],
            supported_output_types=["EvidencePackageContract"],
            dependencies=["python-magic", "SQLAlchemy"]
        ),
        capabilities=[
            "secure_evidence_ingestion",
            "file_signature_validation",
            "sha256_checksum_verification",
            "collision_free_local_storage",
            "chain_of_custody_audit_trails",
            "downstream_dag_routing"
        ],
        custom_configuration_schema={}
    )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Runs the ingestion pipeline for a specific file.
        
        Args:
            context: Active tracing execution context.
            **kwargs: Must contain:
                - file_bytes (bytes): The uploaded file content.
                - filename (str): Original filename.
                - uploader (str): Identity uploader name.
                
        Returns:
            The standard wrapper schema AgentResultContract.
        """
        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        
        warnings: List[str] = []
        errors: List[str] = []
        payload: Dict[str, Any] = {}
        status = "SUCCESS"
        
        # Extrapolate kwargs inputs
        file_bytes = kwargs.get("file_bytes")
        filename = kwargs.get("filename")
        uploader = kwargs.get("uploader")
        
        try:
            # Inputs sanity assertions
            if file_bytes is None:
                raise ValueError("Missing 'file_bytes' parameter.")
            if not filename:
                raise ValueError("Missing 'filename' parameter.")
            if not uploader:
                raise ValueError("Missing 'uploader' parameter.")
                
            # Execute pipeline inside session block
            with get_db_context() as db:
                pipeline = EvidenceIntakePipeline(db)
                package, pipeline_warnings = pipeline.execute(
                    file_bytes=file_bytes,
                    filename=filename,
                    case_id=context.case_id,
                    uploader=uploader
                )
                
                # Update tracking details on context
                context.evidence_id = package.evidence_metadata.evidence_id
                
                payload = package.model_dump()
                warnings.extend(pipeline_warnings)
                
        except EvidenceIntakeError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain validation or storage issue in Intake pipeline: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System failure in Intake Agent run: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        return AgentResultContract(
            agent="evidence_intake",
            status=status,
            processing_context=context,
            payload=payload,
            metrics={
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "processing_time_ms": round(elapsed_ms, 2)
            },
            warnings=warnings,
            errors=errors
        )

    def health(self) -> dict:
        """Reports the health metrics of storage directories and dependency services."""
        return {
            "agent": "evidence_intake",
            "status": "healthy",
            "version": "1.0.0",
            "storage_provider": "local_filesystem"
        }

    def manifest(self) -> AgentManifest:
        """Exposes the capability specification schemas of this intake step."""
        return self._MANIFEST
