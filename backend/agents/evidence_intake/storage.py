# -*- coding: utf-8 -*-
"""Storage abstraction and local file system provider implementation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple
from backend.core.config import settings
from backend.agents.evidence_intake.exceptions import StorageFailureError

class StorageProvider(ABC):
    """Abstract Base Class specifying plug-in storage providers."""
    
    @abstractmethod
    def store(self, file_bytes: bytes, case_id: str, filename: str, sha256_hash: str) -> Tuple[str, str]:
        """Saves file content to the persistent storage layer.
        
        Args:
            file_bytes: Raw binary data.
            case_id: Target Case identifier.
            filename: Sanitized name of the file.
            sha256_hash: Precomputed hash signature.
            
        Returns:
            Tuple of (file_path, object_storage_path).
            
        Raises:
            StorageFailureError: If unable to write/persist the file.
        """
        pass


class LocalStorageProvider(StorageProvider):
    """Concrete storage provider writing evidence files to the local file system."""
    
    def __init__(self, base_dir: Path = settings.STORAGE_DIR) -> None:
        """Initializes the provider with a base storage root.
        
        Args:
            base_dir: Directory path on the local filesystem.
        """
        self.base_dir = Path(base_dir)

    def store(self, file_bytes: bytes, case_id: str, filename: str, sha256_hash: str) -> Tuple[str, str]:
        """Saves file locally using hashed subfolders for scaling and collision avoidance."""
        try:
            # Subdirectory path: cases/{case_id}/evidence/{hash_prefix_1}/{hash_prefix_2}/
            prefix_1 = sha256_hash[:2]
            prefix_2 = sha256_hash[2:4]
            
            target_dir = self.base_dir / "cases" / case_id / "evidence" / prefix_1 / prefix_2
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Append hash to prevent collisions of files with identical names but different hashes
            file_extension = Path(filename).suffix
            unique_filename = f"{sha256_hash}_{filename}"
            target_file_path = target_dir / unique_filename
            
            # Write file block
            with open(target_file_path, "wb") as f:
                f.write(file_bytes)
                
            file_path = str(target_file_path.resolve())
            
            # Simulated object storage path for future MinIO/S3 mapping
            object_storage_path = f"s3://acpia-evidence/cases/{case_id}/{prefix_1}/{prefix_2}/{unique_filename}"
            
            return file_path, object_storage_path
            
        except Exception as e:
            raise StorageFailureError(f"Failed to persist file locally: {e}")
