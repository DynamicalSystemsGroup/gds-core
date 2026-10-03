"""Translate a bounded mathematical grammar to SymPy without evaluating Python."""

from __future__ import annotations

import ast
import keyword
import math
from typing import Any

from gds_domains.symbolic._compat import require_sympy
from gds_domains.symbolic.errors import SymbolicError

MAX_LENGTH = 4096
MAX_NODES = 512
MAX_DEPTH = 64
MAX_INTEGER_BITS = 256

# Explicit arities; no dynamic lookup of names on the SymPy module.
_ARITIES = {
    "sin": (1,),
    "cos": (1,),
    "tan": (1,),
    "asin": (1,),
    "acos": (1,),
    "atan": (1,),
    "sinh": (1,),
    "cosh": (1,),
    "tanh": (1,),
    "exp": (1,),
    "log": (1, 2),
    "sqrt": (1,),
    "Abs": (1,),
}


def make_symbols(names: list[str]) -> dict[str, Any]:
    """Create symbols whose names can safely pass through code generation."""
    require_sympy()
    import sympy

    for name in names:
        if (
            not name.isascii()
            or not name.isidentifier()
            or keyword.iskeyword(name)
            or name.startswith("__")
        ):
            raise SymbolicError(
                "Symbol names must be ASCII Python identifiers without "
                "keywords or a leading double underscore"
            )
    return {name: sympy.Symbol(name) for name in names}


def parse_expression(source: str, symbols: dict[str, Any]) -> Any:
    """Parse only numbers, declared names, arithmetic and approved math calls.

    Validate the entire tree before constructing any SymPy objects. Constructors
    use evaluate=False to defer potentially expensive constant simplification.
    These bounds do not guarantee limits on subsequent symbolic computations.
    """
    if len(source) > MAX_LENGTH:
        raise SymbolicError(f"Expression exceeds {MAX_LENGTH} characters")
    try:
        tree = ast.parse(source.strip(), mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise SymbolicError("Invalid mathematical expression syntax") from exc
    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise SymbolicError(f"Expression exceeds {MAX_NODES} syntax nodes")

    def validate(node: ast.AST, depth: int = 0) -> None:
        if depth > MAX_DEPTH:
            raise SymbolicError(f"Expression exceeds nesting depth {MAX_DEPTH}")
        if isinstance(node, ast.Constant):
            value = node.value
            if type(value) is int:
                if value.bit_length() > MAX_INTEGER_BITS:
                    raise SymbolicError("Integer literal exceeds 256 bits")
            elif type(value) is float:
                if not math.isfinite(value):
                    raise SymbolicError("Numeric literals must be finite")
            else:
                raise SymbolicError("Only real numeric literals are supported")
        elif isinstance(node, ast.Name):
            if node.id not in symbols and node.id not in {"pi", "E"}:
                raise SymbolicError(f"Undeclared symbol: {node.id}")
        elif isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)
        ):
            validate(node.operand, depth + 1)
        elif isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
        ):
            validate(node.left, depth + 1)
            validate(node.right, depth + 1)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id not in _ARITIES:
                raise SymbolicError(f"Unsupported math function: {node.func.id}")
            if node.keywords or len(node.args) not in _ARITIES[node.func.id]:
                raise SymbolicError(f"Invalid arguments for {node.func.id}")
            for arg in node.args:
                validate(arg, depth + 1)
        else:
            raise SymbolicError(f"Unsupported expression syntax: {type(node).__name__}")

    validate(tree.body)
    require_sympy()
    import sympy

    functions = {
        "sin": sympy.sin,
        "cos": sympy.cos,
        "tan": sympy.tan,
        "asin": sympy.asin,
        "acos": sympy.acos,
        "atan": sympy.atan,
        "sinh": sympy.sinh,
        "cosh": sympy.cosh,
        "tanh": sympy.tanh,
        "exp": sympy.exp,
        "log": sympy.log,
        "sqrt": sympy.sqrt,
        "Abs": sympy.Abs,
    }
    constants = {"pi": sympy.pi, "E": sympy.E}

    def build(node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return (
                sympy.Integer(node.value)
                if type(node.value) is int
                else sympy.Float(node.value)
            )
        if isinstance(node, ast.Name):
            return symbols[node.id] if node.id in symbols else constants[node.id]
        if isinstance(node, ast.UnaryOp):
            value = build(node.operand)
            return (
                value
                if isinstance(node.op, ast.UAdd)
                else sympy.Mul(-1, value, evaluate=False)
            )
        if isinstance(node, ast.BinOp):
            left, right = build(node.left), build(node.right)
            if isinstance(node.op, ast.Add):
                return sympy.Add(left, right, evaluate=False)
            if isinstance(node.op, ast.Sub):
                return sympy.Add(
                    left, sympy.Mul(-1, right, evaluate=False), evaluate=False
                )
            if isinstance(node.op, ast.Mult):
                return sympy.Mul(left, right, evaluate=False)
            if isinstance(node.op, ast.Div):
                return sympy.Mul(
                    left, sympy.Pow(right, -1, evaluate=False), evaluate=False
                )
            return sympy.Pow(left, right, evaluate=False)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return functions[node.func.id](
                *(build(arg) for arg in node.args), evaluate=False
            )
        raise AssertionError("Expression tree was not validated")

    try:
        return build(tree.body)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise SymbolicError("Unable to construct mathematical expression") from exc
