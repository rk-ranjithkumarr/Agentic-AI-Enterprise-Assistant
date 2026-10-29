from __future__ import annotations

from pathlib import Path

import fitz
import pandas as pd
from docx import Document as DocxDocument


def _pdf_to_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text_parts: list[str] = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(part for part in text_parts if part)


def _docx_to_text(docx_path: str) -> str:
    document = DocxDocument(docx_path)
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs)


def _txt_to_text(txt_path: str) -> str:
    with open(txt_path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def _csv_to_text(csv_path: str) -> str:
    dataframe = pd.read_csv(csv_path)
    return dataframe.to_string(index=False)


def extract_document_text(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = _pdf_to_text(str(path))
        source_type = "pdf"
    elif suffix == ".docx":
        text = _docx_to_text(str(path))
        source_type = "docx"
    elif suffix in {".txt", ".md"}:
        text = _txt_to_text(str(path))
        source_type = "text"
    elif suffix == ".csv":
        text = _csv_to_text(str(path))
        source_type = "csv"
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return {
        "title": path.name,
        "source_type": source_type,
        "source_path": str(path),
        "text": text,
        "word_count": len(text.split()),
    }


def summarize_text(text: str, max_sentences: int = 3) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return "No text available for summary."
    parts = [segment.strip() for segment in cleaned.split(".") if segment.strip()]
    summary = ". ".join(parts[:max_sentences])
    return f"{summary.rstrip()}." if summary and not summary.endswith(".") else summary


def heading_summary(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    headings = []
    for line in lines:
        if line.endswith(":") or line.lower().startswith(("summary", "purpose", "overview", "result")):
            headings.append(line)
    return headings[:10]


__all__ = ["extract_document_text", "summarize_text", "heading_summary"]
