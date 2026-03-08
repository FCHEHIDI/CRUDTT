"""Fonctions endpoint pour les ressources analytiques (v1)."""

import logging
from typing import Literal

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.analytics import (
    DepartmentCostsResponse,
    ExpensiveToolsResponse,
    LowUsageToolsResponse,
    ToolsByCategoryResponse,
    VendorSummaryResponse,
)
from app.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)


def get_department_costs(
    sort_by: Literal["total_cost", "department"] = Query(
        default="total_cost",
        description="Champ de tri des résultats.",
    ),
    order: Literal["asc", "desc"] = Query(
        default="desc",
        description="Ordre de tri.",
    ),
    db: Session = Depends(get_db),
) -> DepartmentCostsResponse:
    """Répartition des coûts par département.

    Args:
        sort_by: "total_cost" ou "department".
        order: "asc" ou "desc".
        db: Session de base de données injectée.

    Returns:
        DepartmentCostsResponse avec données et summary.
    """
    result = AnalyticsService(db).department_costs(sort_by=sort_by, order=order)
    return DepartmentCostsResponse.model_validate(result)


def get_expensive_tools(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Nombre maximum d'outils retournés (1–100).",
    ),
    min_cost: float | None = Query(
        default=None,
        gt=0,
        description="Filtre coût mensuel minimum.",
    ),
    db: Session = Depends(get_db),
) -> ExpensiveToolsResponse:
    """Top outils coûteux avec rating d'efficacité.

    Args:
        limit: Nombre maximum d'outils (1–100).
        min_cost: Coût mensuel minimum (optionnel).
        db: Session de base de données injectée.

    Returns:
        ExpensiveToolsResponse avec données et analyse globale.
    """
    result = AnalyticsService(db).expensive_tools(limit=limit, min_cost=min_cost)
    return ExpensiveToolsResponse.model_validate(result)


def get_tools_by_category(
    db: Session = Depends(get_db),
) -> ToolsByCategoryResponse:
    """Répartition des outils et coûts par catégorie.

    Args:
        db: Session de base de données injectée.

    Returns:
        ToolsByCategoryResponse avec données et insights.
    """
    result = AnalyticsService(db).tools_by_category()
    return ToolsByCategoryResponse.model_validate(result)


def get_low_usage_tools(
    max_users: int = Query(
        default=5,
        ge=0,
        description="Seuil d'utilisateurs actifs (défaut 5).",
    ),
    db: Session = Depends(get_db),
) -> LowUsageToolsResponse:
    """Outils actifs sous-utilisés avec recommandations d'action.

    Args:
        max_users: Seuil d'utilisateurs actifs (inclus).
        db: Session de base de données injectée.

    Returns:
        LowUsageToolsResponse avec données et analyse des économies.
    """
    result = AnalyticsService(db).low_usage_tools(max_users=max_users)
    return LowUsageToolsResponse.model_validate(result)


def get_vendor_summary(
    db: Session = Depends(get_db),
) -> VendorSummaryResponse:
    """Analyse des fournisseurs d'outils actifs.

    Args:
        db: Session de base de données injectée.

    Returns:
        VendorSummaryResponse avec données et insights fournisseurs.
    """
    result = AnalyticsService(db).vendor_summary()
    return VendorSummaryResponse.model_validate(result)
