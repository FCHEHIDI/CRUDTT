"""Dépendances FastAPI partagées entre les routers."""

import logging
from typing import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """Fournit une session SQLAlchemy via l'injection de dépendances FastAPI.

    Yields:
        Session: Une session SQLAlchemy active, fermée automatiquement après usage.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
