# gds-symbolic

[![PyPI](https://img.shields.io/pypi/v/gds-symbolic)](https://pypi.org/project/gds-symbolic/)
[![Python](https://img.shields.io/pypi/pyversions/gds-symbolic)](https://pypi.org/project/gds-symbolic/)
[![License](https://img.shields.io/github/license/DynamicalSystemsGroup/gds-core)](https://github.com/DynamicalSystemsGroup/gds-core/blob/main/LICENSE)

**SymPy bridge for gds-control** -- symbolic state equations, automatic linearization, and ODE code generation.

## Package Identity

| Distribution | Import | Role |
|---|---|---|
| `gds-symbolic` | `gds_domains.symbolic` | SymPy bridge for `gds-control` models |
| `gds-domains` | `gds_domains.symbolic` | Consolidated domain package distribution |

## What is this?

`gds-symbolic` extends `gds-control`'s `ControlModel` with symbolic mathematics. Instead of writing numerical right-hand side functions by hand, you declare state and output equations as symbolic expressions and let the compiler do the rest.

- **`StateEquation`** -- symbolic expression for `dx/dt` (e.g., `"-k * x + b * u"`)
- **`OutputEquation`** -- symbolic expression for sensor output `y` (e.g., `"x + noise"`)
- **`compile_to_ode()`** -- lambdifies symbolic equations into a callable `ODEFunction` compatible with `gds-continuous`
- **`linearize()`** -- computes Jacobian matrices (A, B, C, D) at an operating point
- **Restricted expression grammar** -- constructs SymPy expressions directly from validated syntax

## When to Use It

Use `gds-symbolic` when a control model's dynamics should be specified as
symbolic equations and then linearized or compiled to ODE functions. Use
`gds-control` alone when numerical callables are enough.

## Architecture

```
gds-control (pip install gds-domains)
|
|  State-space control DSL: State, Input, Sensor, Controller.
|
+-- gds-symbolic (uv add gds-symbolic[sympy])
    |
    |  Symbolic layer: StateEquation, OutputEquation,
    |  compile_to_ode(), linearize().
    |
    +-- gds-continuous (optional integration)
        |
        |  ODE simulation engine: ODEModel, ODESimulation.
```

## Key Types

| Type | Purpose |
|------|---------|
| `StateEquation` | Symbolic `dx_i/dt = expr(x, u, params)` |
| `OutputEquation` | Symbolic `y_i = expr(x, u, params)` |
| `SymbolicControlModel` | Extends `ControlModel` with symbolic equations |
| `ODEFunction` | Lambdified callable: `f(t, x, params) -> dx/dt` |
| `LinearSystem` | Matrices `(A, B, C, D)` from Jacobian linearization |

## How It Works

```
Symbolic expressions (strings)
    |
    v
Validated AST  -->  SymPy Expr objects
    |
    v
compile_to_ode()  -->  ODEFunction (lambdified, math-backed)
    |                       |
    v                       v
linearize()           gds-continuous ODEModel
    |
    v
LinearSystem(A, B, C, D)   -->  eigenvalue analysis, controllability, etc.
```

## Expression grammar and security

ODE compilation, linearization (including output equations), and Hamiltonian
state dynamics and Lagrangian parsing share a restricted expression grammar:

- Integer and finite floating-point literals, including scientific notation.
- Declared state, input, and parameter names; Hamiltonian expressions also
  support `t` and generated costate names.
- Constants `pi` and `E`, unless a declared variable uses the same name.
- Parentheses, `+`, `-`, `*`, `/`, `**`, and unary `+`/`-`.
- One-argument functions `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`,
  `cosh`, `tanh`, `exp`, `sqrt`, and `Abs`; `log` takes one argument or an
  optional second argument for the base.

Use explicit multiplication (`2*x`) and `**` for powers. Unknown symbols,
SymPy constructors such as `Symbol(...)`, attribute access, indexing, Python
statements, arbitrary calls, keyword arguments, and argument unpacking raise
`SymbolicError` when the expressions are consumed. Model construction performs
structural validation; it does not parse expressions. `terminal_cost` is currently
stored but not consumed by Hamiltonian derivation.

The parser validates the complete Python AST and constructs SymPy objects directly;
it does not evaluate the source string. Symbol names must be ASCII Python
identifiers, excluding keywords and names starting with `__`. Code generation uses
`lambdify` with dummy arguments and internally constructed expressions.
`lambdify` itself generates and executes Python code, so arbitrary externally
supplied SymPy objects are outside this expression-string security boundary.

Expressions are limited to 4,096 characters, 512 AST nodes, depth 64, and integer
literals of at most 256 bits. Constant simplification is deferred during parsing.
These checks do not bound all subsequent symbolic differentiation, simplification,
or numerical work. Services processing hostile input should enforce time and
memory limits in an isolated worker.

## Quick Start

```bash
uv add "gds-symbolic[sympy]"
```

See [Getting Started](getting-started.md) for a full walkthrough.

## Relationship to the Ecosystem

`gds-symbolic` sits between the control DSL and continuous-time simulation. It
extends `gds-control` models with SymPy expressions and can produce ODE
functions for `gds-continuous`.

## Credits

Built on [gds-control](../control/index.md) by [DynamicalSystemsGroup](https://dynamicalsystemsgroup.com).
