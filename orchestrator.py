from __future__ import annotations

import re
from typing import Any

from enterprise_app.agents.calculation_agent import CalculationAgent
from enterprise_app.agents.data_analysis_agent import CSVAnalysisAgent
from enterprise_app.agents.document_agent import DocumentSearchAgent
from enterprise_app.agents.report_agent import ReportAgent
from enterprise_app.agents.verification_agent import TaskVerificationAgent
from enterprise_app.database.db import save_tool_result, save_workflow


class WorkflowEngine:
    def __init__(
        self,
        document_agent: DocumentSearchAgent | None = None,
        calculation_agent: CalculationAgent | None = None,
        analysis_agent: CSVAnalysisAgent | None = None,
        report_agent: ReportAgent | None = None,
        verification_agent: TaskVerificationAgent | None = None,
    ) -> None:
        self.document_agent = document_agent or DocumentSearchAgent()
        self.calculation_agent = calculation_agent or CalculationAgent()
        self.analysis_agent = analysis_agent or CSVAnalysisAgent()
        self.report_agent = report_agent or ReportAgent()
        self.verification_agent = verification_agent or TaskVerificationAgent()

    @staticmethod
    def route_task(task: str) -> str:
        lowered = task.lower()
        if any(keyword in lowered for keyword in ["calculate", "sum", "average", "math", "equation", "compute", "+", "-"]):
            return "calculation"
        if any(keyword in lowered for keyword in ["csv", "data", "analy", "dataset", "column", "rows"]):
            return "data_analysis"
        if any(keyword in lowered for keyword in ["document", "search", "research", "pdf", "docx", "report finding", "policy", "file"]):
            return "document_research"
        if any(keyword in lowered for keyword in ["report", "summary", "brief"]):
            return "report"
        return "general"

    @staticmethod
    def extract_expression(task: str) -> str:
        match = re.search(r"[-+*/0-9.\s]+", task)
        if match:
            expr = match.group(0).strip()
            if expr:
                return expr
        return "2 + 2"

    def build_plan(self, task: str) -> list[dict[str, str]]:
        category = self.route_task(task)
        if category == "calculation":
            return [{"name": "calculation", "description": "Evaluate numeric expression"}]
        if category == "data_analysis":
            return [{"name": "data_analysis", "description": "Inspect the provided CSV or dataset"}]
        if category == "document_research":
            return [{"name": "document_search", "description": "Search index for relevant passages"}]
        if category == "report":
            return [{"name": "report", "description": "Generate a structured report"}]
        return [{"name": "report", "description": "Create an evidence-based summary"}]

    def run(self, task: str) -> dict[str, Any]:
        category = self.route_task(task)
        workflow_id = save_workflow(task, category, "in_progress", "Workflow started")
        plan = self.build_plan(task)
        execution_log: list[dict[str, Any]] = []
        summary: dict[str, Any] = {}

        try:
            if category == "document_research":
                result = self.document_agent.search(task, limit=5)
                execution_log.append({"name": "document_search", "status": "completed", "result": result})
                save_tool_result(workflow_id, "document_search", "completed", result)
                summary["documents"] = result
            elif category == "calculation":
                expression = self.extract_expression(task)
                result = self.calculation_agent.evaluate(expression)
                execution_log.append({"name": "calculation", "status": "completed", "result": result})
                save_tool_result(workflow_id, "calculation", "completed", result)
                summary["calculation"] = result
            elif category == "data_analysis":
                csv_path = "sample_data/sample_metrics.csv"
                result = self.analysis_agent.analyze(csv_path)
                execution_log.append({"name": "data_analysis", "status": "completed", "result": result})
                save_tool_result(workflow_id, "data_analysis", "completed", result)
                summary["analysis"] = result
            else:
                result = {"status": "no-specific-agent"}
                execution_log.append({"name": "report", "status": "completed", "result": result})
                save_tool_result(workflow_id, "report", "completed", result)
                summary["report"] = result

            report = self.report_agent.generate_report(
                task=task,
                document_results=summary.get("documents", {}).get("results"),
                calculation_results=summary.get("calculation"),
                analysis_results=summary.get("analysis"),
            )
            execution_log.append({"name": "report", "status": "completed", "result": report})
            save_tool_result(workflow_id, "report", "completed", report)
            verification = self.verification_agent.verify(task, {"category": category, "execution_log": execution_log})

            save_workflow(task, category, "completed", str(report.get("summary", "")))
            return {
                "task": task,
                "category": category,
                "status": "completed",
                "plan": plan,
                "execution_log": execution_log,
                "result": report,
                "verification": verification,
            }
        except Exception as exc:  # pragma: no cover - defensive
            save_tool_result(workflow_id, "workflow", "failed", {"error": str(exc)})
            save_workflow(task, category, "failed", str(exc))
            return {
                "task": task,
                "category": category,
                "status": "failed",
                "plan": plan,
                "execution_log": execution_log,
                "error": str(exc),
            }
