# -*- coding: utf-8 -*-
"""Centralized logging configuration for ACPIA."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.core.config import settings

class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Include exception information if available
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Incorporate extra attributes passed to logging calls
        if hasattr(record, "extra_attrs") and isinstance(record.extra_attrs, dict):
            log_data.update(record.extra_attrs)
            
        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Retrieves or creates a configured logger instance.
    
    Args:
        name: Name of the logger.
        
    Returns:
        A configured logging.Logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatting in production environment, readable formats in development
    if settings.ENVIRONMENT == "production":
        handler.setFormatter(JSONFormatter())
    else:
        dev_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d]: %(message)s"
        )
        handler.setFormatter(dev_formatter)
        
    logger.addHandler(handler)
    logger.propagate = False
    return logger
