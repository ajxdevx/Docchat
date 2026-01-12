from __future__ import annotations

import logging
from pathlib import Path

from ..core.config import Config
from ..infrastructure.database import Database
from ..infrastructure.openai_client import OpenAIClient, OpenAIError
from .documents import chunk_pages, parse_document
from .rag import RagService


class IngestionService:
    def __init__(
        self,
        config: Config,
        database: Database,
        rag: RagService,
        openai: OpenAIClient,
        logger: logging.Logger,
    ):
        self.config = config
        self.database = database
        self.rag = rag
        self.openai = openai
        self.logger = logger

    def ingest(self, document_id: str, user_id: str, file_path: Path, extension: str) -> None:
        try:
            pages = parse_document(file_path, extension)
            settings = self.config.section("chunking")
            chunks = chunk_pages(
                pages,
                int(settings.get("max_words", 500)),
                int(settings.get("overlap_words", 75)),
            )
            max_chunks = int(settings.get("max_chunks_per_document", 8000))
            if len(chunks) > max_chunks:
                raise ValueError(
                    f"The document produced {len(chunks):,} chunks, above the configured limit of {max_chunks:,}. "
                    "Increase chunking.max_chunks_per_document deliberately or reduce the document scope."
                )
            if self.openai.configured:
                try:
                    self.rag.embed_chunks(chunks)
                except OpenAIError:
                    self.logger.warning(
                        "embedding_failed_using_lexical_fallback",
                        exc_info=True,
                        extra={
                            "user_id": user_id,
                            "document_id": document_id,
                            "error_code": "embedding_failed",
                        },
                    )
            self.database.replace_chunks(document_id, user_id, chunks)
            self.database.update_document(
                document_id,
                status="ready",
                page_count=max(page.number for page in pages),
                chunk_count=len(chunks),
                error_message=None,
            )
            self.logger.info(
                "document_ingested",
                extra={"user_id": user_id, "document_id": document_id},
            )
        except Exception as exc:
            self.database.update_document(document_id, status="failed", error_message=str(exc)[:500])
            self.logger.error(
                "document_ingestion_failed",
                exc_info=True,
                extra={
                    "user_id": user_id,
                    "document_id": document_id,
                    "error_code": "ingestion_failed",
                },
            )

