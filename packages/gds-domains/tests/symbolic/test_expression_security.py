"""Exercise expression security through every public parsing entry point."""

from __future__ import annotations

import math
import os

import pytest

pytest.importorskip("sympy")

from gds_domains.control import Input, Sensor, State
from gds_domains.symbolic import (
    OutputEquation,
    StateEquation,
    SymbolicControlModel,
    SymbolicError,
)
from gds_domains.symbolic.hamiltonian import (
    HamiltonianSpec,
    derive_hamiltonian,
)


def exercise(entry: str, expression: str) -> None:
    model = SymbolicControlModel(
        name="security",
        states=[State(name="x")],
        sensors=[Sensor(name="y", observes=["x"])],
        state_equations=[
            StateEquation(
                state_name="x", expr_str="x" if entry == "output" else expression
            )
        ],
        output_equations=[OutputEquation(sensor_name="y", expr_str=expression)]
        if entry == "output"
        else [],
    )
    if entry == "compile":
        model.to_ode_function()
    elif entry in {"state", "output"}:
        model.linearize([0.0], [])
    else:
        derive_hamiltonian(
            {"x": expression if entry == "dynamics" else "x"},
            ["x"],
            [],
            [],
            HamiltonianSpec(lagrangian=expression if entry == "lagrangian" else "0"),
        )


@pytest.mark.parametrize(
    "entry", ["compile", "state", "output", "dynamics", "lagrangian"]
)
@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').getpid()",
        "(__import__('os').getpid(), x)[1]",
        "sin(__import__('os').getpid())",
        "x + (__import__('os').getpid())",
        "(x := __import__('os').getpid())",
        "x + unknown",
        "Symbol('unknown')",
        "x.__class__",
        "(lambda: x)()",
        "[x for x in [1]][0]",
        "sin(x, evaluate=True)",
        "sin(*[x])",
        "sin()",
        "log(x, 2, 3)",
        "x // 2",
        "x % 2",
        "x ^ 2",
        "x if x else 0",
        "True",
        "1j",
        "1e999",
        "'x'",
        "",
        "x; x",
    ],
)
def test_rejects_untrusted_expressions_without_execution(
    entry: str, expression: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def getpid() -> int:
        calls.append(True)
        return 123

    monkeypatch.setattr(os, "getpid", getpid)
    try:
        with pytest.raises(SymbolicError):
            exercise(entry, expression)
    finally:
        assert calls == [], "Expression executed Python before being rejected"


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("sin(x)", math.sin(0.5)),
        ("cos(x)", math.cos(0.5)),
        ("tan(x)", math.tan(0.5)),
        ("asin(x)", math.asin(0.5)),
        ("acos(x)", math.acos(0.5)),
        ("atan(x)", math.atan(0.5)),
        ("sinh(x)", math.sinh(0.5)),
        ("cosh(x)", math.cosh(0.5)),
        ("tanh(x)", math.tanh(0.5)),
        ("exp(x)", math.exp(0.5)),
        ("log(x)", math.log(0.5)),
        ("log(x, 2)", math.log(0.5, 2)),
        ("sqrt(x)", math.sqrt(0.5)),
        ("Abs(-x)", 0.5),
        ("pi + E", math.pi + math.e),
        ("  +x - 2*x / (1 + x**2) + 1e-3  ", 0.5 - 1 / 1.25 + 0.001),
        ("1/2", 0.5),
    ],
)
def test_supported_math_compiles(expression: str, expected: float) -> None:
    model = SymbolicControlModel(
        name="math",
        states=[State(name="x")],
        state_equations=[StateEquation(state_name="x", expr_str=expression)],
    )
    fn, _ = model.to_ode_function()
    assert fn(0.0, [0.5], {}) == [pytest.approx(expected)]


def test_functions_support_symbolic_differentiation() -> None:
    model = SymbolicControlModel(
        name="math",
        states=[State(name="x")],
        sensors=[Sensor(name="y", observes=["x"])],
        state_equations=[StateEquation(state_name="x", expr_str="sin(x)")],
        output_equations=[OutputEquation(sensor_name="y", expr_str="exp(x)")],
    )
    lin = model.linearize([0.0], [])
    assert lin.A == [[1.0]]
    assert lin.C == [[1.0]]
    system = derive_hamiltonian(
        {"x": "sin(x)"}, ["x"], [], [], HamiltonianSpec(lagrangian="x**2")
    )
    assert system.augmented_ode(0.0, [0.0, 2.0], {}) == [0.0, -2.0]


@pytest.mark.parametrize(
    "entry", ["compile", "state", "output", "dynamics", "lagrangian"]
)
@pytest.mark.parametrize(
    "expression",
    ["x" * 4097, "+".join(["x"] * 200), "-" * 66 + "x", str(2**256)],
)
def test_expression_limits(entry: str, expression: str) -> None:
    with pytest.raises(SymbolicError):
        exercise(entry, expression)


@pytest.mark.parametrize(
    "name", ["x); injected() #", "__builtins__", "lambda", "\u03b1"]
)
@pytest.mark.parametrize("role", ["state", "input", "parameter"])
def test_rejects_unsafe_symbol_names(name: str, role: str) -> None:
    state_names = [name] if role == "state" else ["x"]
    input_names = [name] if role == "input" else []
    param_names = [name] if role == "parameter" else []
    model = SymbolicControlModel(
        name="symbols",
        states=[State(name=n) for n in state_names],
        inputs=[Input(name=n) for n in input_names],
        symbolic_params=param_names,
        state_equations=[StateEquation(state_name=state_names[0], expr_str="1")],
    )
    with pytest.raises(SymbolicError):
        model.to_ode_function()
    with pytest.raises(SymbolicError):
        model.linearize([0.0], [0.0] * len(input_names))
    with pytest.raises(SymbolicError):
        derive_hamiltonian(
            {state_names[0]: "1"},
            state_names,
            input_names,
            param_names,
            HamiltonianSpec(lagrangian="0"),
        )


@pytest.mark.parametrize("entry", ["compile", "linearize"])
def test_json_loaded_model_rejects_payload_without_execution(
    entry: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def getpid() -> int:
        calls.append(True)
        return 123

    monkeypatch.setattr(os, "getpid", getpid)
    model = SymbolicControlModel.model_validate_json(
        '{"name":"loaded","states":[{"name":"x"}],'
        '"state_equations":[{"state_name":"x",'
        '"expr_str":"__import__(\'os\').getpid()"}]}'
    )
    try:
        with pytest.raises(SymbolicError):
            if entry == "compile":
                model.to_ode_function()
            else:
                model.linearize([0.0], [])
    finally:
        assert calls == [], "Loading or processing the model executed Python"


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("x" + " " * 4095, 0.5),
        ("+".join(["(x+x)"] * 64), 64.0),
        ("-" * 64 + "x", 0.5),
        (str(2**255), float(2**255)),
    ],
)
def test_valid_expressions_near_limits(expression: str, expected: float) -> None:
    model = SymbolicControlModel(
        name="limits",
        states=[State(name="x")],
        state_equations=[StateEquation(state_name="x", expr_str=expression)],
    )
    fn, _ = model.to_ode_function()
    assert fn(0.0, [0.5], {}) == [pytest.approx(expected)]


@pytest.mark.parametrize(
    "entry", ["compile", "state", "output", "dynamics", "lagrangian"]
)
def test_expression_paths_do_not_use_python_evaluating_parser(
    entry: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sympy.parsing import sympy_parser

    def unsafe_parser(*args, **kwargs):
        raise AssertionError("Expression path used SymPy's Python-evaluating parser")

    monkeypatch.setattr(sympy_parser, "parse_expr", unsafe_parser)
    exercise(entry, "sin(x) + x**2")


def test_symbol_names_cannot_shadow_generated_math_calls() -> None:
    model = SymbolicControlModel(
        name="symbols",
        states=[State(name="sin")],
        symbolic_params=["pi"],
        state_equations=[StateEquation(state_name="sin", expr_str="sin(sin) + pi")],
    )
    fn, _ = model.to_ode_function()
    assert fn(0.0, [0.5], {"pi": 2.0}) == [pytest.approx(math.sin(0.5) + 2.0)]


def test_compatibility_wrapper_rejects_payload() -> None:
    legacy = pytest.importorskip("gds_symbolic")
    model = legacy.SymbolicControlModel(
        name="legacy",
        states=[State(name="x")],
        state_equations=[
            legacy.StateEquation(state_name="x", expr_str="__import__('os').getpid()")
        ],
    )
    with pytest.raises(SymbolicError):
        model.to_ode_function()
