from __future__ import annotations
from enum import Enum
from sqlalchemy import (
    Integer, String, Text, ForeignKey, DateTime, func, CheckConstraint,
    UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class DocumentStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    ready = "ready"
    failed = "failed"

def StatusType():
    # For SQLite/general case — pseudo-Enum string with CHECK
    return String(32)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "status in ('queued','processing','ready','failed')",
            name="ck_documents_status_valid"
        ),
        {"sqlite_autoincrement": True},
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    original_name: Mapped[str] = mapped_column(String(255))  # name provided by the customer
    stored_name: Mapped[str] = mapped_column(String(255))  # name in storage (UUID и e.t.)
    mime: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)  # size
    sha256: Mapped[str] = mapped_column(String(64), index=True)  # for deduplication
    path: Mapped[str] = mapped_column(String(1024))  # path/key to the repository
    status: Mapped[str] = mapped_column(StatusType(), default=DocumentStatus.queued.value, index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)  # ISO-639-1 type 'en','uk','ru'
    ingested_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    processed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan", order_by="DocumentChunk.seq"
    )

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "seq", name="uq_document_chunks_doc_seq"),
        Index("ix_chunks_doc_seq", "document_id", "seq"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    seq: Mapped[int] = mapped_column(Integer)  # порядковий номер чанка
    text: Mapped[str] = mapped_column(Text)
    # Optional useful field to cut by pages if collecting:
    page_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_to: Mapped[int | None] = mapped_column(Integer, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")