"""Routeur principal v1 — agrège tous les routers de ressources."""

import logging

from fastapi import APIRouter

from app.api.v1.routers import tool as tool_router
from app.api.v1.routers import analytics as analytics_router

logger = logging.getLogger(__name__)

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(tool_router.router)
api_v1_router.include_router(analytics_router.router)