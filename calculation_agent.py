from __future__ import annotations

import ast
import math
from typing import Any


_ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "exp": math.exp,
    "fabs": math.fabs,
}

_ALLOWED_BIN_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
    ast.Mod: lambda a, b: a % b,
}

_ALLOWED_UNARY_OPS = {
    ast.UAdd: lambda a: +a,
    ast.USub: lambda a: -a,
}


class CalculationAgent:
    """Safely evaluate an arithmetic expression using a vetted AST."""

    def evaluate(self, expression: str) -> dict[str, Any]:
        if not expression or not expression.strip():
            raise ValueError("Expression cannot be empty.")

        expr = expression.strip()
        parsed = ast.parse(expr, mode="eval")

        def _evaluate(node: ast.AST) -> Any:
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN_OPS:
                left = _evaluate(node.left)
                right = _evaluate(node.right)
                return _ALLOWED_BIN_OPS[type(node.op)](left, right)
            if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPS:
                operand = _evaluate(node.operand)
                return _ALLOWED_UNARY_OPS[type(node.op)](operand)
            if isinstance(node, ast.Name) and node.id in _ALLOWED_NAMES:
                return _ALLOWED_NAMES[node.id]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_NAMES:
                args = [_evaluate(arg) for arg in node.args]
                if len(args) == 1:
                    return _ALLOWED_NAMES[node.func.id](args[0])
                raise ValueError(f"Function '{node.func.id}' requires exactly one argument.")
            raise ValueError(f"Unsupported expression: {expr}")

        result = _evaluate(parsed.body)
        return {
            "expression": expr,
            "result": result,
            "details": f"Evaluated expression '{expr}' to {result}.",
        }
