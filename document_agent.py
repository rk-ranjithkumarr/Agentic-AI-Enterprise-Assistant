from __future__ import annotations

from pathlib import Path
from typing import Any

from enterprise_app.rag.indexer import DocumentIndexer
from enterprise_app.services.document_service import extract_document_text, heading_summary, summarize_text


class DocumentSearchAgent:
    def __init__(self, indexer: DocumentIndexer | None = None) -> None:
        self.indexer = indexer or DocumentIndexer()

    def index_document(self, file_path: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = extract_document_text(file_path)
        document_id = str(Path(file_path).stem)
        self.indexer.add_document(
            document_id=document_id,
            title=payload["title"],
            text=payload["text"],
            source_type=payload["source_type"],
            source_path=payload["source_path"],
        )
        summary = summarize_text(payload["text"])
        return {
            "document_id": document_id,
            "title": payload["title"],
            "source_type": payload["source_type"],
            "source_path": payload["source_path"],
            "word_count": payload["word_count"],
            "summary": summary,
            "headings": heading_summary(payload["text"]),
        }

    def search(self, query: str, limit: int = 5) -> dict[str, Any]:
        results = self.indexer.search(query, limit=limit)
        return {
            "query": query,
            "total_matches": len(results),
            "results": results,
        }

    def summarise_documents(self) -> dict[str, Any]:
        summaries = self.indexer.summarize_documents()
        return {"summaries": summaries}
