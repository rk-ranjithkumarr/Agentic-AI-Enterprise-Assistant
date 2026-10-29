from __future__ import annotations

from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def chunk_text(text: str, chunk_size: int = 300) -> list[str]:
    paragraphs = [segment.strip() for segment in text.replace("\r", "").split("\n") if segment.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for paragraph in paragraphs:
        if current_length + len(paragraph) > chunk_size and current:
            chunks.append(" ".join(current))
            current = [paragraph]
            current_length = len(paragraph)
        else:
            current.append(paragraph)
            current_length += len(paragraph)
    if current:
        chunks.append(" ".join(current))
    return chunks or [text[:chunk_size] if text else ""]


class DocumentIndexer:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    def add_document(self, document_id: str, title: str, text: str, source_type: str, source_path: str) -> dict[str, Any]:
        if not text.strip():
            raise ValueError("Document text is empty; nothing to index.")
        chunks = chunk_text(text)
        record = {
            "document_id": document_id,
            "title": title,
            "source_type": source_type,
            "source_path": source_path,
            "chunks": chunks,
            "count": len(chunks),
        }
        for index, chunk in enumerate(chunks):
            self.documents.append(
                {
                    "document_id": document_id,
                    "title": title,
                    "source_type": source_type,
                    "source_path": source_path,
                    "text": chunk,
                    "chunk_index": index,
                    "score": 0.0,
                }
            )
        return record

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")
        if not self.documents:
            return []

        corpus = [item["text"] for item in self.documents]
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(corpus + [query.strip()])
        similarities = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
        ranked_indices = similarities.argsort()[::-1][:limit]

        results: list[dict[str, Any]] = []
        for idx in ranked_indices:
            if similarities[idx] <= 0:
                continue
            doc = dict(self.documents[idx])
            doc["score"] = round(float(similarities[idx]), 4)
            results.append(doc)
        return results

    def summarize_documents(self) -> list[str]:
        if not self.documents:
            return []
        grouped: dict[str, list[str]] = {}
        for item in self.documents:
            grouped.setdefault(item["document_id"], []).append(item["text"])
        summaries: list[str] = []
        for doc_id, chunks in grouped.items():
            text = " ".join(chunks)
            preview = text[:220].strip()
            summaries.append(f"{doc_id}: {preview}...")
        return summaries
