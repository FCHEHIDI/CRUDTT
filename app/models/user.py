"""Modèle ORM User."""

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class User(Base):
    """Représente un utilisateur dans la base de données.

    Attributes:
        id: Identifiant unique.
        username: Nom d'utilisateur unique.
        email: Adresse email unique.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
