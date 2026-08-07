# -*- coding: utf-8 -*-
"""Metadata extractor dispatcher."""

from typing import Dict, Type, Any, Optional
from backend.agents.metadata.exceptions import UnsupportedMetadataError
from backend.agents.metadata.extractors.generic_extractor import GenericExtractor
from backend.agents.metadata.extractors.image_extractor import ImageExtractor
from backend.agents.metadata.extractors.video_extractor import VideoExtractor
from backend.agents.metadata.extractors.audio_extractor import AudioExtractor
from backend.agents.metadata.extractors.document_extractor import DocumentExtractor
from backend.agents.metadata.constants import MIME_GROUPS

class MetadataDispatcher:
    """Dispatches files to specific extractor classes based on MIME classifications."""
    
    def __init__(self, custom_extractors: Optional[Dict[str, Type[Any]]] = None) -> None:
        """Initializes the dispatcher with mapping rules.
        
        Args:
            custom_extractors: Override default mime group extractor mappings.
        """
        # Default mappings
        self._extractor_map: Dict[str, Type[Any]] = {
            "image": ImageExtractor,
            "video": VideoExtractor,
            "audio": AudioExtractor,
            "document": DocumentExtractor,
        }
        if custom_extractors:
            self._extractor_map.update(custom_extractors)

    def select_extractor(self, mime_type: str) -> Type[Any]:
        """Resolves the correct extractor class for a given MIME type.
        
        Args:
            mime_type: File signature MIME type string.
            
        Returns:
            The extractor class type.
            
        Raises:
            UnsupportedMetadataError: For invalid or blocked formats.
        """
        if not mime_type:
            raise UnsupportedMetadataError("MIME type string is empty.")
            
        normalized_mime = mime_type.lower().strip()
        
        # Match MIME against registered category groups
        for category, mimes in MIME_GROUPS.items():
            if normalized_mime in mimes:
                extractor_cls = self._extractor_map.get(category)
                if extractor_cls:
                    return extractor_cls
                    
        # Default fallback for unmapped or generic files (e.g. text logs, bin data)
        return GenericExtractor
