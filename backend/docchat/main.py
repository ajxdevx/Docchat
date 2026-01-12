from __future__ import annotations

import sqlite3
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.router import register_routes
from .runtime import build_context


def create_app(config_path: str | Path | None = None) -> FastAPI:
    project_root = Path(__file__).resolve().parents[2]
    context = build_context(config_path or project_root / "config.yaml")
    app_settings = context.config.section("app")
    author_cfg = app_settings.get("author") or {}
    app = FastAPI(
        title=str(app_settings.get("name", "DocChat Local")),
        version=str(app_settings.get("version", "0.1.0")),
        description=str(app_settings.get("description", "")),
        contact={
            "name": str(author_cfg.get("name", "Ajxdevx")),
            "email": str(author_cfg.get("email", "Ajxfuture@gmail.com")),
        },
    )
    app.state.context = context

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["x-request-id"] = request_id
            return response
        finally:
            context.logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "user_id": getattr(request.state, "user_id", None),
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )

    @app.exception_handler(sqlite3.IntegrityError)
    async def integrity_error_handler(_: Request, __: sqlite3.IntegrityError):
        return JSONResponse(status_code=409, content={"detail": "That record already exists"})

    register_routes(app)

    if context.frontend_path.exists():
        app.mount("/static", StaticFiles(directory=context.frontend_path), name="static")

        @app.get("/", include_in_schema=False)
        def index() -> FileResponse:
            return FileResponse(context.frontend_path / "index.html")

    return app


app = create_app()
