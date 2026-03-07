"""Fonctions endpoint pour les ressources utilisateurs (v1)."""

import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

logger = logging.getLogger(__name__)


def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Crée un nouvel utilisateur.

    Args:
        payload: Données de création validées par Pydantic.
        db: Session de base de données injectée.

    Returns:
        L'utilisateur créé.

    Raises:
        HTTPException: 409 si l'email existe déjà.
    """
    service = UserService(db)
    if service.get_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà.",
        )
    return service.create(payload)


def list_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[UserRead]:
    """Liste les utilisateurs avec pagination.

    Args:
        skip: Nombre d'éléments à ignorer.
        limit: Nombre maximum d'éléments à retourner.
        db: Session de base de données injectée.

    Returns:
        Liste d'utilisateurs.
    """
    return UserService(db).get_all(skip=skip, limit=limit)


def get_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    """Récupère un utilisateur par son ID.

    Args:
        user_id: Identifiant de l'utilisateur.
        db: Session de base de données injectée.

    Returns:
        L'utilisateur trouvé.

    Raises:
        HTTPException: 404 si l'utilisateur n'existe pas.
    """
    user = UserService(db).get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé.",
        )
    return user


def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """Supprime un utilisateur.

    Args:
        user_id: Identifiant de l'utilisateur.
        db: Session de base de données injectée.

    Raises:
        HTTPException: 404 si l'utilisateur n'existe pas.
    """
    if not UserService(db).delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé.",
        )
