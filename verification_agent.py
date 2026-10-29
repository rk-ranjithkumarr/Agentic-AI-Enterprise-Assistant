from __future__ import annotations

from typing import Any


class TaskVerificationAgent:
    def verify(self, task: str, workflow_result: dict[str, Any]) -> dict[str, Any]:
        category = workflow_result.get("category", "general")
        required_steps = {
            "document_research": ["document_search"],
            "calculation": ["calculation"],
            "data_analysis": ["data_analysis"],
            "report": ["report"],
            "general": ["report"],
        }
        expected = required_steps.get(category, ["report"])
        actual = workflow_result.get("execution_log", [])
        actual_names = [step.get("name") for step in actual if isinstance(step, dict)]

        missing = [step for step in expected if step not in actual_names]
        status = "passed" if not missing else "failed"

        return {
            "task": task,
            "category": category,
            "status": status,
            "checks": {
                "required_steps": expected,
                "completed_steps": actual_names,
            },
            "missing_evidence": missing,
        }
