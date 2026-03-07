"""Schémas Pydantic pour le modèle User."""

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    """Schéma de création d'un utilisateur.

    Attributes:
        username: Nom d'utilisateur (3-50 caractères).
        email: Adresse email valide.
    """

    username: str
    email: str


class UserRead(BaseModel):
    """Schéma de lecture d'un utilisateur.

    Attributes:
        id: Identifiant unique.
        username: Nom d'utilisateur.
        email: Adresse email.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
