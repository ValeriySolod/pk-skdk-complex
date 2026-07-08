"""Integrations module manifest."""

from fastapi import APIRouter

from app.core.module_registry import ModuleManifest

from .routes import router


def get_router() -> APIRouter:
    return router


manifest = ModuleManifest(
    code="integrations",
    title="Integrations",
    description="Email/API integrations and external service connections.",
    router_factory=get_router,
    permissions=["integrations:read"],
)
