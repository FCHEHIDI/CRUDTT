"""Schémas Pydantic pour le modèle Tool."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.tool import DepartmentEnum, ToolStatusEnum


# Entrée 

class ToolCreate(BaseModel):
    """Schéma pour la création d'un outil."""

    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    vendor: str = Field(..., max_length=100)
    website_url: str | None = None 
    category_id: int = Field(..., gt=0)
    monthly_cost: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    owner_department: DepartmentEnum

    @field_validator("website_url")
    @classmethod
    def validate_website_url(cls, v: str | None) -> str | None:
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        return v
    
class ToolUpdate(BaseModel):
    """Schéma pour la mise à jour d'un outil."""
    name: str | None = Field(default=None, min_length=2, max_length=100)# un outil doit avoir un nom sinon problème!!
    description: str | None = None
    vendor: str | None = Field(default=None, max_length=100)
    website_url: str | None = None
    category_id: int | None = Field(default=None, gt=0)
    monthly_cost: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    owner_department: DepartmentEnum | None = None
    status: ToolStatusEnum | None = None

    @field_validator("website_url") # On répète encore ? Il peut pas traverser les deux classes ?
    @classmethod
    def validate_website_url(cls, v: str | None) -> str | None:
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        return v
    
    # Sortie 

class ToolRead(BaseModel):
    """Schéma pour la lecture d'un outil."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    vendor: str | None
    category: str
    monthly_cost: Decimal
    owner_department: str
    status: str
    website_url: str | None
    active_users_count: int
    created_at: datetime| None


class UsageMetrics(BaseModel):
    """Schéma pour les métriques d'utilisation d'un outil."""
    total_sessions: int
    avg_session_minutes: float


class ToolDetail(ToolRead):
    """Schéma détaillé pour la lecture d'un outil, incluant les métriques d'utilisation."""
    updated_at: datetime | None
    total_monthly_cost: Decimal
    usage_metrics: dict[str, UsageMetrics] # clé "last_30_days" ou "last_7_days" ou "last_24_hours"


class ToolListResponse(BaseModel):
    """Schéma pour la réponse de la liste d'outils."""
    data: list[ToolRead]
    total: int
    filtered: int
    filters_applied: dict[str, Any]