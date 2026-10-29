# Agentic AI Enterprise Assistant

This project provides a locally-run enterprise assistant built with Python, Streamlit, SQLite, and lightweight retrieval techniques. It is designed to run without paid APIs, Docker, or Ollama.

## Features

- Document upload and indexing for TXT, CSV, PDF, and DOCX files
- Local retrieval with TF-IDF similarity search
- Numeric calculation agent with safe expression validation
- CSV analysis agent for column statistics and missing-value detection
- Workflow orchestration and verification
- SQLite-backed persistence for metadata and workflow records
- Streamlit dashboard with task submission, document management, and reports

## Local setup

On Windows, run:

```bat
setup.bat
run.bat
```

## Testing

```bat
test.bat
```

## Notes

- The project intentionally avoids cloud services and external AI APIs.
- Database and uploaded files are stored under the local project directory.
- The system uses deterministic workflows rather than conjectured generative intelligence.
