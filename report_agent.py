from __future__ import annotations

from typing import Any


class ReportAgent:
    def generate_report(self, task: str, document_results: list[dict[str, Any]] | None = None, calculation_results: dict[str, Any] | None = None, analysis_results: dict[str, Any] | None = None) -> dict[str, Any]:
        evidence = []
        if document_results:
            evidence.extend(
                {
                    "type": "document",
                    "source": item.get("source_path") or item.get("title"),
                    "summary": item.get("text")[:180] if isinstance(item.get("text"), str) else item.get("summary"),
                }
                for item in document_results
            )
        if calculation_results:
            evidence.append({
                "type": "calculation",
                "source": "calculator",
                "summary": calculation_results.get("details", "Calculated value was produced."),
            })
        if analysis_results:
            evidence.append({
                "type": "analysis",
                "source": "csv-analysis",
                "summary": f"Analyzed {analysis_results.get('rows', 0)} rows across {len(analysis_results.get('columns', []))} columns.",
            })

        summary = [
            f"Task: {task}",
            f"Evidence gathered: {len(evidence)} source(s)",
        ]
        if calculation_results:
            summary.append(f"Calculated result: {calculation_results.get('result')}")
        if analysis_results:
            summary.append(f"Data points: {analysis_results.get('rows', 0)} rows")

        return {
            "title": f"Report for: {task}",
            "summary": " ".join(summary),
            "evidence": evidence,
            "recommendations": [
                "Review sources for completeness before final action.",
                "Validate numbers against raw source data when precision matters.",
            ],
        }
