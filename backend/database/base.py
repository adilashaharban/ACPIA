# -*- coding: utf-8 -*-
"""SQLAlchemy base class initialization."""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Declarative Base class for all SQLAlchemy database models."""
    pass
