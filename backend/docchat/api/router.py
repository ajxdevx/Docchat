"""Register all HTTP routers on the FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI

from .routes import auth, conversations, documents, health, messages


def register_routes(app: FastAPI) -> None:
    """Mount resource routers in a stable, documented order."""
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(conversations.router)
    app.include_router(messages.router)
