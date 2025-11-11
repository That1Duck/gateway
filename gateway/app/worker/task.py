# app/worker/tasks.py
import os,dramatiq
from dramatiq.brokers.redis import RedisBroker
from ..services.pipeline import process_document

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
dramatiq.set_broker(RedisBroker(url=REDIS_URL))

@dramatiq.actor(max_retries=3)
def parse_document_async(document_id: int):
    process_document(document_id)

"""
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).get(document_id)
        if not doc:
            return
        doc.status = DocumentStatus.processing.value
        db.commit()

        meta, chunks = parse_any(doc.path, doc.mime)  # meta: dict, chunks: list[dict{seq,text,page_from,page_to}]

        # сохранить метаданные
        doc.page_count = meta.get("page_count")
        doc.title = meta.get("title")
        doc.author = meta.get("author")
        doc.language = meta.get("language")

        # сохранить чанки
        for ch in chunks:
            db.add(DocumentChunk(
                document_id=doc.id,
                seq=ch["seq"],
                text=ch["text"],
                page_from=ch.get("page_from"),
                page_to=ch.get("page_to"),
            ))
        doc.status = DocumentStatus.ready.value
        db.commit()
    except Exception as e:
        db.rollback()
        doc = db.query(Document).get(document_id)
        if doc:
            doc.status = DocumentStatus.failed.value
            doc.error = str(e)[:2000]
            db.commit()
    finally:
        db.close()
"""