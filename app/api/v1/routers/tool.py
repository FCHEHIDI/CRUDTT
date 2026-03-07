from fastapi import APIRouter, status

from app.api.v1.endpoints.tool import create_tool, get_tool, list_tools, update_tool
from app.schemas.tool import ToolDetail, ToolListResponse

_ERR_400 = {"description": "Données invalides", "content": {"application/json": {"example": {"erreur": "Validation échouée", "details": {"field": "message"}}}}}
_ERR_404 = {"description": "Outil introuvable", "content": {"application/json": {"example": {"erreur": "Outil non trouvé.", "message": "Aucun outil avec l'ID 1 n'existe."}}}}
_ERR_409 = {"description": "Conflit — nom déjà existant", "content": {"application/json": {"example": {"erreur": "Outil déjà existant.", "message": "Un outil avec le nom 'Slack' existe déjà."}}}}

router = APIRouter(prefix="/tools", tags=["tools"])

router.add_api_route(
    "/",
    list_tools,
    methods=["GET"],
    response_model=ToolListResponse,
    summary="Lister les outils",
    description=(
        "Retourne la liste paginée des outils SaaS avec filtres optionnels.\n\n"
        "**Filtres disponibles** : `department`, `status`, `category`, `min_cost`, `max_cost`\n\n"
        "**Tri** : `sort_by` (name | monthly_cost | created_at) + `order` (asc | desc)\n\n"
        "**Pagination** : `page` (défaut 1) + `limit` (défaut 100)"
    ),
)
router.add_api_route(
    "/",
    create_tool,
    methods=["POST"],
    response_model=ToolDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un outil",
    description="Crée un nouvel outil SaaS. Le statut est forcé à `active` et `active_users_count` démarre à 0.",
    responses={400: _ERR_400, 409: _ERR_409},
)
router.add_api_route(
    "/{tool_id}",
    get_tool,
    methods=["GET"],
    response_model=ToolDetail,
    summary="Détail d'un outil",
    description="Retourne le détail complet d'un outil : métriques d'utilisation sur 30 jours et coût total mensuel.",
    responses={404: _ERR_404},
)
router.add_api_route(
    "/{tool_id}",
    update_tool,
    methods=["PUT"],
    response_model=ToolDetail,
    summary="Mettre à jour un outil",
    description="Mise à jour partielle (PATCH-like) : seuls les champs fournis sont modifiés.",
    responses={400: _ERR_400, 404: _ERR_404},
)