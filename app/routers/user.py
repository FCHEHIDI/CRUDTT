"""Endpoints CRUD pour les utilisateurs."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Crée un nouvel utilisateur.

    Args:
        payload: Données de création.
        db: Session de base de données.

    Returns:
        L'utilisateur créé.

    Raises:
        HTTPException: 409 si l'email ou le username existe déjà.
    """
    service = UserService(db)
    existing = service.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà.",
        )
    return service.create(payload)


@router.get("/", response_model=list[UserRead])
def list_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[UserRead]:
    """Liste les utilisateurs avec pagination.

    Args:
        skip: Nombre d'éléments à ignorer.
        limit: Nombre maximum d'éléments à retourner.
        db: Session de base de données.

    Returns:
        Liste d'utilisateurs.
    """
    service = UserService(db)
    return service.get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    """Récupère un utilisateur par son ID.

    Args:
        user_id: Identifiant de l'utilisateur.
        db: Session de base de données.

    Returns:
        L'utilisateur trouvé.

    Raises:
        HTTPException: 404 si l'utilisateur n'existe pas.
    """
    service = UserService(db)
    user = service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé.",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """Supprime un utilisateur.

    Args:
        user_id: Identifiant de l'utilisateur.
        db: Session de base de données.

    Raises:
        HTTPException: 404 si l'utilisateur n'existe pas.
    """
    service = UserService(db)
    deleted = service.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé.",
        )
