# Symbolic Math (`gds-domains`)

[![PyPI](https://img.shields.io/pypi/v/gds-domains)](https://pypi.org/project/gds-domains/)
[![Python](https://img.shields.io/pypi/pyversions/gds-domains)](https://pypi.org/project/gds-domains/)
[![License](https://img.shields.io/github/license/DynamicalSystemsGroup/gds-core)](https://github.com/DynamicalSystemsGroup/gds-core/blob/main/LICENSE)

**SymPy bridge for `gds_domains.control`** -- symbolic state equations, automatic linearization, and ODE code generation.

## Package Identity

| Distribution | Import | Role |
|---|---|---|
| `gds-domains[symbolic]` | `gds_domains.symbolic` | Current symbolic implementation for control models |
| `gds-symbolic` | `gds_symbolic` | Deprecated compatibility package; use `gds-domains[symbolic]` for new projects |

## What is this?

`gds_domains.symbolic` extends `gds_domains.control`'s `ControlModel` with symbolic mathematics. Instead of writing numerical right-hand side functions by hand, you declare state and output equations as symbolic expressions and let the compiler do the rest.

- **`StateEquation`** -- symbolic expression for `dx/dt` (e.g., `"-k * x + b * u"`)
- **`OutputEquation`** -- symbolic expression for sensor output `y` (e.g., `"x + noise"`)
- **`model.to_ode_function()`** -- returns an ODE callable and its state order, compatible with `gds-continuous`
- **`model.linearize()`** -- computes Jacobian matrices (A, B, C, D) at an operating point
- **Restricted expression grammar** -- constructs SymPy expressions directly from validated syntax

## When to Use It

Use `gds_domains.symbolic` when a control model's dynamics should be specified as
symbolic equations and then linearized or compiled to ODE functions. Use
`gds_domains.control` alone when numerical callables are enough.

## Architecture

```
gds_domains.control (pip install gds-domains)
|
|  State-space control DSL: State, Input, Sensor, Controller.
|
+-- gds_domains.symbolic (uv add "gds-domains[symbolic]>=0.1.1")
    |
    |  Symbolic layer: StateEquation, OutputEquation,
    |  model.to_ode_function(), model.linearize().
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
| `ODEFunction` | Lambdified callable: `f(t, y, params) -> list[float]`, with states in the returned order |
| `LinearizedSystem` | Matrices `(A, B, C, D)` as lists of lists from Jacobian linearization |

## How It Works

```text
SymbolicControlModel: declared states, inputs, parameters, and expressions
    |
    +-- validated AST --> directly constructed SymPy expressions
                              |
                              +-- to_ode_function() --> (ode_fn, state_order)
                              |                          |
                              |                          v
                              |                    gds-continuous ODEModel
                              |
                              +-- linearize(x0, u0, param_values)
                                       |
                                       v
                                LinearizedSystem(A, B, C, D)
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
uv add "gds-domains[symbolic]>=0.1.1"
```

`gds-symbolic>=0.99.1` remains available for existing applications using the
legacy `gds_symbolic` import. It requires the fixed `gds-domains` implementation.

See [Getting Started](getting-started.md) for a full walkthrough.

## Relationship to the Ecosystem

`gds_domains.symbolic` sits between the control DSL and continuous-time simulation. It
extends `gds_domains.control` models with SymPy expressions and can produce ODE
functions for `gds-continuous`.

## Credits

Built on the [control DSL](../control/index.md) by [DynamicalSystemsGroup](https://dynamicalsystemsgroup.com).
