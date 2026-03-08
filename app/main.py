"""Point d'entrée de l'application FastAPI."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.routers import api_v1_router


logger = logging.getLogger(__name__)

# ── Metadata OpenAPI ──────────────────────────────────────────────────────────

DESCRIPTION = """
## Internal Tools Management API

API de gestion des outils SaaS internes d'une entreprise.
Permet de **lister**, **consulter**, **créer** et **mettre à jour** les outils
utilisés par les différents départements.

### Fonctionnalités

- **Filtrage** par département, statut, catégorie et coût mensuel
- **Tri** par nom, coût ou date de création
- **Pagination** configurable
- **Métriques d'utilisation** par outil (sessions, durée moyenne)
- **Coût total mensuel** calculé automatiquement


### Codes d'erreur

| Code | Signification |
|------|---------------|
| `400` | Données invalides (validation Pydantic) |
| `404` | Ressource introuvable |
| `409` | Conflit — ressource déjà existante |
| `500` | Erreur interne serveur |
"""

TAGS_METADATA = [
    {
        "name": "tools",
        "description": (
            "Gestion des outils SaaS. "
            "Opérations : lister avec filtres, consulter le détail, créer, mettre à jour."
        ),
    },
    {
        "name": "analytics",
        "description": (
            "Analytics & reporting des outils SaaS. "
            "Répartition des coûts, outils coûteux, analyse par catégorie, "
            "outils sous-utilisés et analyse fournisseurs."
        ),
    },
    {
        "name": "health",
        "description": "Vérification de l'état de l'application.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application (startup / shutdown)."""
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    contact={
        "name": "Fares Chehidi",
        "email": "Fares_Chehidi@outlook.com",
    },
    license_info={
        "name": "Propriétaire — usage interne uniquement",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_v1_router)


# ── Error handlers ──────────────────────────────────────────────────────────── 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Transforme les erreurs Pydantic 422 en 400 avec format uniforme."""
    details = {}
    for error in exc.errors():
        field = str(error["loc"][-1])
        details[field] = error["msg"]
    return JSONResponse(
        status_code=400,
        content={"erreur": "Validation échouée", "details": details},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    """Capture toute exception non gérée et retourne un 500 propre."""
    logger.error("Erreur inattendue: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"erreur": "Une erreur interne est survenue."},
    )


@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    response_description="Statut de l'application",
    responses={
        200: {
            "description": "Application opérationnelle",
            "content": {
                "application/json": {
                    "example": {"status": "ok", "app": "Internal Tools API"}
                }
            },
        }
    },
)
async def root():
    """Vérifie que l'API est opérationnelle.

    Returns:
        Un objet JSON avec le statut et le nom de l'application.
    """
    return {"status": "ok", "app": settings.APP_NAME}