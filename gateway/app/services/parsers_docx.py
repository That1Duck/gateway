# app/services/parsers_docx.py
from typing import Tuple, Dict, List
from docx import Document as Docx

def parse_docx(path: str) -> Tuple[Dict, List[Dict]]:
    d = Docx(path)
    meta = {
        "title": d.core_properties.title,
        "author": d.core_properties.author,
        "page_count": None,  # docx не хранит страницы; можно вычислять эвристикой при необходимости
    }
    text = "\n".join(p.text for p in d.paragraphs if p.text)
    # простейший чанк — весь текст единым блоком; при желании режем по 2–4k символов
    chunks = [{"seq": 0, "text": text, "page_from": None, "page_to": None}] if text.strip() else []
    return meta, chunks
