# app/schemas/document.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class DocumentStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class DocumentCreate(BaseModel):
    user_id: int
    original_name: str
    mime: str
    size_bytes: int
    sha256: str
    stored_name: str
    path: str

class DocumentChunkOut(BaseModel):
    id: int
    seq: int
    text: str
    page_from: Optional[int] = None
    page_to: Optional[int] = None

    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    user_id: int
    original_name: str
    stored_name: str
    mime: str
    size_bytes: int
    sha256: str
    path: str
    status: DocumentStatus
    error: Optional[str] = None
    page_count: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    ingested_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    progress_percent: Optional[int] = 0

    class Config: from_attributes = True

    class Config:
        from_attributes = True

class DocumentWithChunksOut(DocumentOut):
    chunks: List[DocumentChunkOut] = []
