from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, Response, UploadFile

from ...runtime import AppContext
from ..dependencies import current_user, get_context
from ..helpers import require_document, safe_document

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("")
def list_documents(
    search: str = Query(default="", max_length=120),
    user: dict[str, Any] = Depends(current_user),
    context: AppContext = Depends(get_context),
) -> list[dict[str, Any]]:
    return [safe_document(item) for item in context.database.list_documents(user["id"], search)]


@router.post("", status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(current_user),
    context: AppContext = Depends(get_context),
) -> dict[str, Any]:
    filename = Path(file.filename or "document").name
    extension = Path(filename).suffix.lower()
    upload_settings = context.config.section("uploads")
    allowed = {str(item).lower() for item in upload_settings.get("allowed_extensions", [])}
    if extension not in allowed:
        raise HTTPException(status_code=415, detail=f"Allowed file types: {', '.join(sorted(allowed))}")
    max_bytes = int(upload_settings.get("max_file_mb", 50)) * 1024 * 1024
    storage_path = context.uploads_path / f"{uuid.uuid4()}{extension}"
    size = 0
    try:
        with storage_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(status_code=413, detail="The file is larger than the configured limit")
                output.write(chunk)
    except Exception:
        storage_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    mime_type = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    document = context.database.create_document(
        user_id=user["id"],
        filename=filename,
        storage_path=str(storage_path),
        extension=extension,
        mime_type=mime_type,
        size_bytes=size,
    )
    background_tasks.add_task(
        context.ingestion.ingest,
        document["id"],
        user["id"],
        storage_path,
        extension,
    )
    return safe_document(document)


@router.get("/{document_id}")
def get_document(
    document_id: str,
    user: dict[str, Any] = Depends(current_user),
    context: AppContext = Depends(get_context),
) -> dict[str, Any]:
    return safe_document(require_document(context, document_id, user["id"]))


@router.post("/{document_id}/reindex", status_code=202)
def reindex_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    user: dict[str, Any] = Depends(current_user),
    context: AppContext = Depends(get_context),
) -> dict[str, Any]:
    document = require_document(context, document_id, user["id"])
    context.database.update_document(document_id, status="processing", error_message=None)
    background_tasks.add_task(
        context.ingestion.ingest,
        document_id,
        user["id"],
        Path(document["storage_path"]),
        document["extension"],
    )
    return {"id": document_id, "status": "processing"}


@router.delete("/{document_id}", status_code=204, response_class=Response)
def delete_document(
    document_id: str,
    user: dict[str, Any] = Depends(current_user),
    context: AppContext = Depends(get_context),
) -> Response:
    document = require_document(context, document_id, user["id"])
    if context.database.delete_document(document_id, user["id"]):
        Path(document["storage_path"]).unlink(missing_ok=True)
    return Response(status_code=204)
