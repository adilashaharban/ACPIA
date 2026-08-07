# -*- coding: utf-8 -*-
"""Generic filesystem metadata extractor."""

import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from backend.agents.metadata.exceptions import ParserFailureError
from backend.agents.metadata.schema import FileMetadata

class GenericExtractor:
    """Extracts general operating system filesystem properties of evidence files."""
    
    @staticmethod
    def extract(file_path: str) -> FileMetadata:
        """Reads file attributes from the local filesystem.
        
        Args:
            file_path: Absolute string path of the target file.
            
        Returns:
            A populated FileMetadata model.
            
        Raises:
            ParserFailureError: If file details cannot be accessed.
        """
        path = Path(file_path)
        if not path.exists():
            raise ParserFailureError(f"Target evidence file does not exist: {file_path}")
            
        try:
            stat_result = path.stat()
            
            # File size
            size_bytes = stat_result.st_size
            
            # File permissions
            permissions = stat.filemode(stat_result.st_mode)
            
            # Timestamps
            mtime = datetime.fromtimestamp(stat_result.st_mtime, timezone.utc)
            
            # Use birthtime if available, fall back to ctime
            try:
                ctime = datetime.fromtimestamp(stat_result.st_birthtime, timezone.utc)
            except AttributeError:
                ctime = datetime.fromtimestamp(stat_result.st_ctime, timezone.utc)
                
            return FileMetadata(
                file_size_bytes=size_bytes,
                file_permissions=permissions,
                creation_time=ctime,
                modification_time=mtime
            )
        except Exception as e:
            raise ParserFailureError(f"Failed to read file attributes for {file_path}: {e}")
