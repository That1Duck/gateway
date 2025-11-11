import os
import hashlib
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.document import Document, DocumentStatus, DocumentChunk
from ...schemas.document import DocumentOut, DocumentWithChunksOut, DocumentChunkOut
from ...worker.task import parse_document_async

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_file(user_id: int = Form(...),
                      f: UploadFile = File(...),
                      db: Session = Depends(get_db)):
    # валидация MIME/размера по настройкам
    data = await f.read()
    size = len(data)
    sha256 = hashlib.sha256(data).hexdigest()
    original = f.filename
    stored = f"{uuid4().hex}_{original}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, stored)
    with open(path, "wb") as out:
        out.write(data)

    doc = Document(
        user_id=user_id,
        original_name=original,
        stored_name=stored,
        mime=f.content_type or "application/octet-stream",
        size_bytes=size,
        sha256=sha256,
        path=path,
        status=DocumentStatus.queued.value,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # отправляем задачу в очередь
    try:
        parse_document_async.send(doc.id)
    except Exception as e:
        # если брокер недоступен — можно пометить failed или оставить queued и отретраить позже
        doc.status = DocumentStatus.failed.value
        doc.error = f"enqueue failed: {e}"
        db.commit()
        raise

    return doc

@router.get("/{doc_id}", response_model=DocumentWithChunksOut)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc