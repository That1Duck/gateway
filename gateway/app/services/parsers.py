# app/services/parsers.py
from typing import Tuple, Dict, List
import os, subprocess, tempfile
from ..services.parsers_pdf import parse_pdf
from ..services.parsers_docx import parse_docx

def parse_any(path: str, mime: str) -> Tuple[Dict, List[Dict]]:
    ext = os.path.splitext(path)[1].lower()

    if mime == "application/pdf" or ext == ".pdf":
        return parse_pdf(path)

    if mime in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ) or ext == ".docx":
        return parse_docx(path)

    # .doc или неизвестное → конвертим в docx/pdf через LibreOffice
    if ext == ".doc":
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["soffice", "--headless", "--convert-to", "docx", "--outdir", tmp, path], check=True)
            new_path = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + ".docx")
            return parse_docx(new_path)

    # как универсальный запасной вариант можно подключить Tika
    raise ValueError(f"Unsupported format: {mime} ({ext})")
