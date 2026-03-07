"""Modèle ORM Tool."""

import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, func, Numeric, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class DepartmentEnum(str, enum.Enum):
    """Enumération des départements d'une entreprise."""

    Engineering = "Engineering"
    Sales = "Sales"
    Marketing = "Marketing"
    HR = "HR"
    Finance = "Finance"
    Operations = "Operations"
    Design = "Design"

class ToolStatusEnum(str, enum.Enum):
    """Enumération des statuts d'un outil SaaS."""

    active = "active"
    deprecated = "deprecated"
    trial = "trial"

class Tool(Base):
    """Représente un outil SaaS dans la base de données.

    Attributes:
        id: Identifiant unique.
        name: Nom de l'outil.
        description: Description détaillée de l'outil.
        vendor: Nom du fournisseur de l'outil.
        website_url: URL du site web de l'outil.
        category_id: Clé étrangère vers la catégorie de l'outil.
        monthly_cost: Coût mensuel de l'outil en dollars.
        active_users_count: Nombre d'utilisateurs actifs utilisant l'outil.
        owner_department: Département propriétaire de l'outil (enum).
        status: Statut de l'outil (enum).
        created_at: Date et heure de création de l'enregistrement.
        updated_at: Date et heure de la dernière mise à jour de l'enregistrement.
    """

    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    vendor = Column(String(100), nullable=True)
    website_url = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    monthly_cost = Column(Numeric(10, 2), nullable=False)
    active_users_count = Column(Integer, nullable=False, default=0)
    owner_department = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="tools")