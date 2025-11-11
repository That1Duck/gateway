# app/services/parsers_pdf.py
from typing import Tuple, Dict, List
import pdfplumber

def parse_pdf(path: str) -> Tuple[Dict, List[Dict]]:
    chunks: List[Dict] = []
    meta: Dict = {}

    with pdfplumber.open(path) as pdf:
        meta["page_count"] = len(pdf.pages)
        # Вытянуть title/author, если есть:
        doc_meta = pdf.metadata or {}
        meta["title"] = doc_meta.get("Title")
        meta["author"] = doc_meta.get("Author")

        seq = 0
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            # чанкуем по страницам; можно далее резать по N символов
            if text.strip():
                chunks.append({"seq": seq, "text": text, "page_from": i, "page_to": i})
                seq += 1

    return meta, chunks
