"""Routeur utilisateurs v1 — lie les handlers aux routes HTTP."""

import logging

from fastapi import APIRouter, status

from app.api.v1.endpoints.user import create_user, delete_user, get_user, list_users
from app.schemas.user import UserRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

router.add_api_route(
    "/",
    create_user,
    methods=["POST"],
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un utilisateur",
)
router.add_api_route(
    "/",
    list_users,
    methods=["GET"],
    response_model=list[UserRead],
    summary="Lister les utilisateurs",
)
router.add_api_route(
    "/{user_id}",
    get_user,
    methods=["GET"],
    response_model=UserRead,
    summary="Récupérer un utilisateur",
)
router.add_api_route(
    "/{user_id}",
    delete_user,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur",
)
