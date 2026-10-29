from __future__ import annotations

from pathlib import Path

from enterprise_app.config import DATA_DIR, DB_PATH, PROJECT_ROOT, UPLOAD_DIR
from enterprise_app.database.db import initialize_database


def run_checks() -> dict[str, object]:
    initialize_database()
    issues: list[str] = []
    if not PROJECT_ROOT.exists():
        issues.append("Project root is missing.")
    if not DATA_DIR.exists():
        issues.append("Data directory is missing.")
    if not UPLOAD_DIR.exists():
        issues.append("Upload directory is missing.")
    if not Path(DB_PATH).exists():
        issues.append("Database file was not created.")
    return {
        "status": "ok" if not issues else "error",
        "issues": issues,
        "database": str(DB_PATH),
    }


if __name__ == "__main__":
    result = run_checks()
    print(result)
