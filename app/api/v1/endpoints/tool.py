"""Fonctions endpoint pour les outils SaaS (v1)"""

import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.tool import ToolCreate, ToolRead, ToolUpdate, ToolDetail, ToolListResponse
from app.services.tool import ToolService

logger = logging.getLogger(__name__)

def list_tools(
    department: str | None = None,
    status: str | None = None,
    category: str | None = None,
    min_cost: float | None = None,
    max_cost: float | None = None,
    sort_by: str = "name",
    order: str = "asc",
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> ToolListResponse:
    """Liste les outils avec filtres, tri et pagination.""" 
    return ToolService(db).get_all(
        department=department,
        status=status,
        category=category,
        min_cost=min_cost,
        max_cost=max_cost,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit,
    )

def get_tool(tool_id: int, db: Session = Depends(get_db)) -> ToolDetail:
    """Récupère un outil par son ID."""
    tool = ToolService(db).get_by_id(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"erreur": "Outil non trouvé.", "message": f"Aucun outil avec l'ID {tool_id} n'existe."},
        )
    return tool

def create_tool(payload: ToolCreate, db: Session = Depends(get_db)) -> ToolDetail:
    """Crée un nouvel outil."""
    service = ToolService(db)
    if service.get_by_name(payload.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"erreur": "Outil déjà existant.", "message": f"Un outil avec le nom '{payload.name}' existe déjà."},
        )
    if not service.category_exists(payload.category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"erreur": "Catégorie invalide.", "message": f"Aucune catégorie avec l'ID {payload.category_id} n'existe."},
        )
    return service.create(payload)

def update_tool(tool_id: int, payload: ToolUpdate, db: Session = Depends(get_db)) -> ToolDetail:
    """Met à jour un outil existant."""
    service = ToolService(db)
    if payload.category_id and not service.category_exists(payload.category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"erreur": "Catégorie invalide.", "message": f"Aucune catégorie avec l'ID {payload.category_id} n'existe."},
        )
    tool = service.update(tool_id, payload)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"erreur": "Outil non trouvé.", "message": f"Aucun outil avec l'ID {tool_id} n'existe."},
        )
    return tool