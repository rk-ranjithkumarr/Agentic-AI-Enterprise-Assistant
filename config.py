from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "enterprise_app"
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "enterprise_assistant.db"
SAMPLE_DATA_DIR = PROJECT_ROOT / "sample_data"

for directory in (DATA_DIR, UPLOAD_DIR, SAMPLE_DATA_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    return value
