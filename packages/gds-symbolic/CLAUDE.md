# CLAUDE.md -- gds-symbolic

## Package Identity

`gds-symbolic` extends `gds-control`'s `ControlModel` with symbolic differential equations (SymPy). Compiles symbolic ODEs to plain Python callables via `sympy.lambdify` for use with `gds-continuous`.

- **Import**: `import gds_symbolic`
- **Dependencies**: `gds-framework>=0.2.3`, `gds-control>=0.1.0`, `pydantic>=2.10`
- **Optional**: `[sympy]` for SymPy + numpy, `[continuous]` for gds-continuous

## Architecture

| Module | Purpose |
|--------|---------|
| `elements.py` | `StateEquation`, `OutputEquation` — frozen Pydantic models storing `expr_str` (R1-serializable) |
| `model.py` | `SymbolicControlModel(ControlModel)` — adds symbolic equations + validation |
| `compile.py` | `compile_to_ode(model)` → `(ODEFunction, state_order)` via validated AST construction + `lambdify` |
| `linearize.py` | `linearize(model, x0, u0)` → `LinearizedSystem(A, B, C, D)` via Jacobians |
| `transfer.py` | `ss_to_tf()`, `poles()`, `zeros()`, `controllability_matrix()`, `sensitivity()` (Gang of Six) |
| `delay.py` | `pade_approximation()`, `delay_system()` — Padé time delay modeling |
| `errors.py` | `SymbolicError(CSError)` — inherits control domain error hierarchy |

### Security

Use the shared parser in `gds_domains.symbolic._expressions` for expression
strings. It validates an allowlist of AST nodes, names and math calls, then builds
SymPy expressions directly. Symbol creation uses `make_symbols`; numerical code
generation uses `lambdify(..., dummify=True)`. Keep all expression entry points on
this path. The grammar and computational limits are documented in
`docs/symbolic/index.md`; parsing limits do not bound subsequent symbolic work.

### R1/R2/R3 boundary

- `StateEquation.expr_str` (string) → R1, serializable to OWL
- `sympy.Expr` (parsed) → R2, transient
- Lambdified callable → R3, opaque

### Transfer function analysis (`transfer.py`)

Builds on `LinearizedSystem` (A, B, C, D as `list[list[float]]`):
- `ss_to_tf(ls)` → `TransferFunctionMatrix` via adjugate/determinant method
- `poles(tf)`, `zeros(tf)` → `list[complex]` via SymPy roots
- `controllability_matrix(ls)`, `observability_matrix(ls)` → Kalman rank matrices
- `sensitivity(plant, controller)` → Gang of Six: S, T, CS, PS, KS, KPS

### Padé time delay (`delay.py`)

- `pade_approximation(delay, order)` → all-pass `TransferFunction` approximating e^{-sτ}
- `delay_system(tf, delay, order)` → cascaded TF with Padé delay

### Known limitations

- Inputs resolved from constant `params` — no time-varying signals (see gds-continuous CLAUDE.md)
- `compile()` and `compile_system()` remain structural — symbolic equations don't appear in GDSSpec
- `poles()`/`zeros()` use SymPy's symbolic root finder — may return incomplete results for degree > 4
- Transfer functions use the full characteristic polynomial as denominator (MIMO elements share the same denominator)

## Commands

```bash
uv run --package gds-symbolic pytest packages/gds-symbolic/tests -v
```
