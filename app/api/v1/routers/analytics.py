"""Routeur analytics v1 — lie les handlers aux routes HTTP avec metadata Swagger."""

import logging

from fastapi import APIRouter, status

from app.api.v1.endpoints.analytics import (
    get_department_costs,
    get_expensive_tools,
    get_low_usage_tools,
    get_tools_by_category,
    get_vendor_summary,
)
from app.schemas.analytics import (
    DepartmentCostsResponse,
    ExpensiveToolsResponse,
    LowUsageToolsResponse,
    ToolsByCategoryResponse,
    VendorSummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

_ERR_400 = {
    400: {
        "description": "Paramètre invalide",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "error": "Invalid analytics parameter",
                        "details": {"limit": "Must be positive integer between 1 and 100"},
                    }
                }
            }
        },
    }
}

router.add_api_route(
    "/department-costs",
    get_department_costs,
    methods=["GET"],
    response_model=DepartmentCostsResponse,
    status_code=status.HTTP_200_OK,
    summary="Répartition des coûts par département",
    description=(
        "Agrège les coûts des outils **actifs** par département propriétaire.\n\n"
        "- `cost_percentage` = (département.total_cost / company.total_cost) × 100\n"
        "- `average_cost_per_tool` = total_cost / tools_count\n"
        "- `most_expensive_department` : département avec le plus haut total_cost "
        "(ordre alphabétique en cas d'égalité)"
    ),
)

router.add_api_route(
    "/expensive-tools",
    get_expensive_tools,
    methods=["GET"],
    response_model=ExpensiveToolsResponse,
    status_code=status.HTTP_200_OK,
    summary="Top outils les plus coûteux",
    description=(
        "Retourne les outils actifs triés par coût décroissant avec un rating d'efficacité.\n\n"
        "**efficiency_rating** basé sur cost_per_user vs moyenne entreprise :\n"
        "- `excellent` : < 50 % de la moyenne\n"
        "- `good` : 50–80 %\n"
        "- `average` : 80–120 %\n"
        "- `low` : > 120 % (ou 0 utilisateurs)\n\n"
        "`potential_savings_identified` = somme des monthly_cost des outils `low`."
    ),
    responses=_ERR_400,
)

router.add_api_route(
    "/tools-by-category",
    get_tools_by_category,
    methods=["GET"],
    response_model=ToolsByCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Répartition des outils par catégorie",
    description=(
        "Agrège les outils actifs par catégorie avec coût total, utilisateurs et pourcentage budget.\n\n"
        "- `most_efficient_category` : catégorie avec le plus bas `average_cost_per_user` "
        "(catégories sans utilisateurs exclues)"
    ),
)

router.add_api_route(
    "/low-usage-tools",
    get_low_usage_tools,
    methods=["GET"],
    response_model=LowUsageToolsResponse,
    status_code=status.HTTP_200_OK,
    summary="Outils sous-utilisés",
    description=(
        "Identifie les outils actifs avec peu d'utilisateurs et calcule les économies potentielles.\n\n"
        "**warning_level** basé sur cost_per_user :\n"
        "- `high` : > 50 €/user ou 0 utilisateurs → *Consider canceling or downgrading*\n"
        "- `medium` : 20–50 €/user → *Review usage and consider optimization*\n"
        "- `low` : < 20 €/user → *Monitor usage trends*\n\n"
        "`potential_monthly_savings` = somme des coûts des outils `high` + `medium`."
    ),
)

router.add_api_route(
    "/vendor-summary",
    get_vendor_summary,
    methods=["GET"],
    response_model=VendorSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse des fournisseurs",
    description=(
        "Agrège les outils actifs par fournisseur avec départements et rating d'efficacité.\n\n"
        "**vendor_efficiency** basé sur average_cost_per_user :\n"
        "- `excellent` : < 5 €/user\n"
        "- `good` : 5–15 €/user\n"
        "- `average` : 15–25 €/user\n"
        "- `poor` : > 25 €/user\n\n"
        "`departments` : départements uniques triés alphabétiquement, séparés par virgule.\n"
        "`single_tool_vendors` : vendors ayant exactement 1 outil actif (opportunités de consolidation)."
    ),
)
