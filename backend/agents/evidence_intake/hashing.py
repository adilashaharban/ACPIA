# -*- coding: utf-8 -*-
"""Stream-safe SHA-256 hashing utility."""

import hashlib
from backend.agents.evidence_intake.exceptions import HashingError

class EvidenceHasher:
    """Computes SHA-256 checksums to verify integrity and detect duplicates."""
    
    @staticmethod
    def compute_hash(data: bytes) -> str:
        """Calculates the SHA-256 hex digest of a byte stream.
        
        Args:
            data: Raw binary data.
            
        Returns:
            The 64-character hex digest of the SHA-256 hash.
            
        Raises:
            HashingError: If hashing calculation fails.
        """
        if data is None:
            raise HashingError("Data buffer is None.")
            
        try:
            hasher = hashlib.sha256()
            # Stream bytes in chunks to handle memory safely
            chunk_size = 65536  # 64KB chunks
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            raise HashingError(f"Failed to compute SHA-256 hash: {e}")
