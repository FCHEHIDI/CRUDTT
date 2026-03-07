"""Modèle ORM Category."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    """Représente une catégorie d'outils SaaS.

    Attributes:
        id: Identifiant unique.
        name: Nom de la catégorie (unique).
        description: Description textuelle.
        color_hex: Couleur d'affichage en hexadécimal.
        created_at: Date de création.
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color_hex = Column(String(7), default="#6366f1")

    tools = relationship("Tool", back_populates="category")
