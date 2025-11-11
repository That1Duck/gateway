import logging
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..models.document import Document, DocumentStatus, DocumentChunk
from ..services.parsers import parse_any

log = logging.getLogger(__name__)

def _update(doc: Document, db: Session, *, status=None, progress=None, processed_by=None):
    if status is not None: doc.status = status
    if progress is not None: doc.progress_percent = max(0, min(100, int(progress)))
    if processed_by is not None: doc.processed_by = processed_by
    db.commit()

def process_document(document_id: int) -> None:
    db: Session = SessionLocal()
    try:
        doc = db.get(Document, document_id)
        if not doc:
            return
        # идемпотентность на случай ретраев/дубликатов
        if doc.status in (DocumentStatus.processing.value, DocumentStatus.ready.value):
            return

        log.info("doc %s: start", document_id)
        _update(doc, db, status=DocumentStatus.processing.value, progress=0, processed_by="pipeline@1.0")

        meta, chunks = parse_any(doc.path, doc.mime)
        doc.page_count = meta.get("page_count")
        doc.title = meta.get("title")
        doc.author = meta.get("author")
        doc.language = meta.get("language")
        _update(doc, db, progress=80)

        for i, ch in enumerate(chunks):
            db.add(DocumentChunk(
                document_id=doc.id,
                seq=ch.get("seq", i),
                text=ch["text"],
                page_from=ch.get("page_from"),
                page_to=ch.get("page_to"),
            ))
        doc.status = DocumentStatus.ready.value
        doc.progress_percent = 100
        db.commit()
        log.info("doc %s: ready", document_id)
    except Exception as e:
        db.rollback()
        doc = db.get(Document, document_id)
        if doc:
            doc.status = DocumentStatus.failed.value
            doc.error = str(e)[:2000]
            db.commit()
        log.exception("doc %s: failed: %s", document_id, e)
    finally:
        db.close()
