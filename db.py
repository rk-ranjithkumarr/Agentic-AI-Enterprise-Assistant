from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

from enterprise_app.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                source_type TEXT NOT NULL,
                uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'indexed'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER,
                tool_name TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def record_document(title: str, file_name: str, file_path: str, source_type: str) -> dict[str, Any]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO documents (title, file_name, file_path, source_type, status)
            VALUES (?, ?, ?, ?, 'indexed')
            """,
            (title, file_name, file_path, source_type),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "title": title,
            "file_name": file_name,
            "file_path": file_path,
            "source_type": source_type,
        }
    finally:
        conn.close()


def list_documents() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, file_name, file_path, source_type, uploaded_at, status FROM documents ORDER BY uploaded_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def remove_document(doc_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
    finally:
        conn.close()


def save_workflow(task: str, category: str, status: str, details: str | None = None) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO workflows (task, category, status, details) VALUES (?, ?, ?, ?)",
            (task, category, status, details),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def save_tool_result(workflow_id: int, tool_name: str, status: str, payload: str | dict[str, Any] | None) -> None:
    conn = get_connection()
    try:
        payload_text = str(payload) if payload is not None else None
        conn.execute(
            "INSERT INTO tool_results (workflow_id, tool_name, status, payload) VALUES (?, ?, ?, ?)",
            (workflow_id, tool_name, status, payload_text),
        )
        conn.commit()
    finally:
        conn.close()


def save_conversation(role: str, content: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO conversations (role, content) VALUES (?, ?)",
            (role, content),
        )
        conn.commit()
    finally:
        conn.close()


def safe_sql_query(query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("Query cannot be empty.")
    if not cleaned.lower().startswith("select"):
        raise ValueError("Only SELECT queries are permitted for safe read-only execution.")
    conn = get_connection()
    try:
        rows = conn.execute(cleaned, tuple(params)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
