from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from enterprise_app.agents.orchestrator import WorkflowEngine
from enterprise_app.config import UPLOAD_DIR
from enterprise_app.database.db import initialize_database, list_documents, record_document, remove_document, save_conversation
from enterprise_app.rag.indexer import DocumentIndexer
from enterprise_app.agents.document_agent import DocumentSearchAgent

st.set_page_config(page_title="Agentic AI Enterprise Assistant", layout="wide")

initialize_database()

if "document_agent" not in st.session_state:
    st.session_state.document_agent = DocumentSearchAgent(indexer=DocumentIndexer())
if "workflow_history" not in st.session_state:
    st.session_state.workflow_history = []


def persist_uploaded_documents(uploaded_files):
    for uploaded_file in uploaded_files:
        upload_path = UPLOAD_DIR / uploaded_file.name
        upload_path.write_bytes(uploaded_file.getvalue())
        record_document(
            title=uploaded_file.name,
            file_name=uploaded_file.name,
            file_path=str(upload_path),
            source_type=Path(uploaded_file.name).suffix.lower().lstrip("."),
        )
        st.session_state.document_agent.index_document(str(upload_path))


st.title("Agentic AI Enterprise Assistant")
st.caption("Deterministic workflow orchestration for document intelligence, calculations, and reporting.")

with st.sidebar:
    st.header("Controls")
    uploaded_files = st.file_uploader("Upload documents", type=["pdf", "docx", "txt", "csv"], accept_multiple_files=True)
    if uploaded_files:
        persist_uploaded_documents(uploaded_files)

    if st.button("Reset database"):
        db_path = Path(UPLOAD_DIR).parent / "enterprise_assistant.db"
        if db_path.exists():
            db_path.unlink()
        initialize_database()
        st.session_state.workflow_history = []
        st.session_state.document_agent = DocumentSearchAgent(indexer=DocumentIndexer())
        st.success("Database reset complete.")

    st.subheader("Application health")
    st.info("SQLite initialized and ready for use.")

left, right = st.columns([1.5, 1])

with left:
    st.subheader("Workflow task")
    task = st.text_area("Describe the task or question", placeholder="Example: Calculate 12 * 7 and summarize the result.")
    if st.button("Run workflow"):
        if task.strip():
            engine = WorkflowEngine(document_agent=st.session_state.document_agent)
            result = engine.run(task)
            st.session_state.workflow_history.append(result)
            save_conversation("user", task)
            save_conversation("assistant", json.dumps(result, default=str))
            st.success("Workflow completed.")
        else:
            st.warning("Please provide a task before running the workflow.")

    if st.session_state.workflow_history:
        last_result = st.session_state.workflow_history[-1]
        st.subheader("Workflow output")
        st.json(last_result)

with right:
    st.subheader("Indexed documents")
    docs = list_documents()
    if docs:
        for doc in docs:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"{doc['title']} ({doc['source_type']})")
            with col_b:
                if st.button("Remove", key=f"remove-{doc['id']}"):
                    remove_document(doc["id"])
                    st.rerun()
    else:
        st.write("No documents uploaded yet.")

    st.subheader("Workflow timeline")
    for history in st.session_state.workflow_history:
        st.write(f"- {history.get('category', 'general')}: {history.get('status', 'unknown')}")
