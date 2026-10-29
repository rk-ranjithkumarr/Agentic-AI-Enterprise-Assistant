from __future__ import annotations

from enterprise_app.agents.calculation_agent import CalculationAgent
from enterprise_app.agents.data_analysis_agent import CSVAnalysisAgent
from enterprise_app.agents.document_agent import DocumentSearchAgent
from enterprise_app.rag.indexer import DocumentIndexer
from enterprise_app.agents.orchestrator import WorkflowEngine


def test_calculation_agent_evaluates_expression():
    result = CalculationAgent().evaluate("12 * 7")
    assert result["result"] == 84


def test_csv_analysis_agent_reads_sample_data():
    analysis = CSVAnalysisAgent().analyze("sample_data/sample_metrics.csv")
    assert analysis["rows"] == 5
    assert "profit" in analysis["columns"]


def test_document_search_agent_can_index_and_search():
    agent = DocumentSearchAgent(indexer=DocumentIndexer())
    agent.index_document("sample_data/enterprise_notes.txt")
    results = agent.search("finance team monitors expenses", limit=3)
    assert results["total_matches"] >= 1


def test_workflow_route_task():
    assert WorkflowEngine.route_task("calculate 7 plus 5") == "calculation"
    assert WorkflowEngine.route_task("analyze CSV profitability") == "data_analysis"
    assert WorkflowEngine.route_task("research enterprise policy") == "document_research"
