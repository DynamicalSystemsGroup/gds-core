# gds-domains

Domain-specific languages for the [GDS ecosystem](https://github.com/DynamicalSystemsGroup/gds-core).

## Subpackages

- `gds_domains.stockflow` — Stock-flow system dynamics DSL
- `gds_domains.control` — State-space control systems DSL
- `gds_domains.business` — Business dynamics DSL (CLD, supply chain, VSM)
- `gds_domains.software` — Software architecture DSL (DFD, state machine, component, C4, ERD, dependency)
- `gds_domains.games` — Compositional game theory DSL
- `gds_domains.symbolic` — SymPy bridge for symbolic control models

## Installation

```bash
pip install gds-domains                          # base (stockflow, control, business, software)
pip install gds-domains[games]                   # + typer CLI, Jinja2 reports
pip install gds-domains[symbolic]                # + SymPy
pip install gds-domains[nashpy]                  # + Nash equilibrium
pip install gds-domains[all]                     # everything
```

## Symbolic expressions

Symbolic compilation and analysis accept a restricted mathematical grammar:
declared variables, numeric literals, arithmetic, and approved math functions.
Unsupported syntax raises `SymbolicError` when an expression is consumed.
See the [expression grammar and security limits](https://dynamicalsystemsgroup.github.io/gds-core/symbolic/#expression-grammar-and-security)
for supported functions, symbol naming rules, and resource limits. Parsing limits
do not bound all subsequent symbolic computations.
