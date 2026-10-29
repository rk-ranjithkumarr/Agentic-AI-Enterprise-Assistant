from __future__ import annotations

from typing import Any

import pandas as pd


class CSVAnalysisAgent:
    def analyze(self, csv_path: str) -> dict[str, Any]:
        dataframe = pd.read_csv(csv_path)
        missing_values = dataframe.isna().sum().to_dict()
        numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()

        summary: dict[str, Any] = {
            "rows": int(len(dataframe)),
            "columns": list(dataframe.columns),
            "numeric_columns": numeric_columns,
            "missing_values": {str(key): int(value) for key, value in missing_values.items()},
            "shape": [int(dataframe.shape[0]), int(dataframe.shape[1])],
            "duplicate_rows": int(dataframe.duplicated().sum()),
            "sample_head": dataframe.head(5).to_dict(orient="records"),
        }

        if numeric_columns:
            stats = dataframe[numeric_columns].describe().to_dict()
            summary["statistics"] = {key: {inner_key: float(value) if isinstance(value, (int, float)) else value for inner_key, value in inner.items()} for key, inner in stats.items()}
        else:
            summary["statistics"] = {}

        return summary
