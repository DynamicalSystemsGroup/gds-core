# Getting Started

## Installation

For new projects, install the current symbolic implementation:

```bash
uv add "gds-domains[symbolic]>=0.1.1"
```

`gds-symbolic` is a deprecated compatibility package. Existing users should
upgrade it to at least `0.99.1`; new code uses `gds_domains.symbolic`.

For development in the monorepo:

```bash
git clone https://github.com/DynamicalSystemsGroup/gds-core.git
cd gds-core
uv sync --all-packages --all-extras
```

## Your First Symbolic Model

Declare the states, input, sensor, and symbolic parameter names before writing
expressions. This damped oscillator has position `x1`, velocity `x2`, and an
external force `u`.

```python
from gds_domains.control import Input, Sensor, State
from gds_domains.symbolic import (
    OutputEquation,
    StateEquation,
    SymbolicControlModel,
)

model = SymbolicControlModel(
    name="DampedOscillator",
    states=[State(name="x1", initial=1.0), State(name="x2", initial=0.0)],
    inputs=[Input(name="u")],
    sensors=[Sensor(name="position", observes=["x1"])],
    symbolic_params=["k", "c"],
    state_equations=[
        StateEquation(state_name="x1", expr_str="x2"),
        StateEquation(state_name="x2", expr_str="-k*x1 - c*x2 + u"),
    ],
    output_equations=[OutputEquation(sensor_name="position", expr_str="x1")],
)

ode_fn, state_order = model.to_ode_function()
print(state_order)  # ['x1', 'x2']
dx = ode_fn(0.0, [1.0, 0.0], {"k": 4.0, "c": 0.5, "u": 0.0})
print(dx)  # [0.0, -4.0]
```

The callable takes `(t, y, params)` and returns a derivative list. `y` follows
`state_order`; input and parameter values are supplied in `params`. Declaring
`symbolic_params` does not bind their numerical values. Pass all values needed
for an analysis explicitly; unspecified inputs and parameters default to zero.

Expressions use the [restricted mathematical grammar](index.md#expression-grammar-and-security).
Use `state_name` / `sensor_name` and `expr_str` for equation fields. Arbitrary
Python calls and unknown symbols are rejected when expressions are consumed.

## Integration with gds-continuous

Install the SciPy integration extra for this section:

```bash
uv add "gds-continuous[scipy]"
```

Continue with the `model`, `ode_fn`, and `state_order` from above:

```python
from gds_continuous import ODEModel, ODESimulation

ode_model = ODEModel(
    state_names=state_order,
    initial_state={"x1": 1.0, "x2": 0.0},
    rhs=ode_fn,
    params={"k": [4.0], "c": [0.5], "u": [0.0]},
)

sim = ODESimulation(
    model=ode_model,
    t_span=(0.0, 20.0),
    t_eval=[i / 10 for i in range(201)],
    solver="RK45",
)
results = sim.run()
print(results.times[0], results.state_array("x1")[0])  # 0.0 1.0
```

`ODEModel.params` takes lists of candidate values and expands their Cartesian
product into simulation subsets. Singleton lists above request one trajectory.
Use `results.times` and `results.state_array(name)` to read a trajectory.
`results.to_list()` exposes row dictionaries with `time`, `run`, `subset`, and
state columns; `results.to_dataframe()` additionally requires the pandas extra.

For an optional plot, install Matplotlib with `uv add matplotlib` and run:

```python
import matplotlib.pyplot as plt

plt.plot(results.times, results.state_array("x1"), label="position")
plt.plot(results.times, results.state_array("x2"), label="velocity")
plt.legend()
plt.title("Damped Harmonic Oscillator")
plt.xlabel("Time")
plt.grid(True)
plt.show()
```

## Linearization

Use state and input vectors in declaration order, with explicit parameter
values, to compute the Jacobian matrices at an operating point:

```python
lin = model.linearize(
    x0=[0.0, 0.0],
    u0=[0.0],
    param_values={"k": 4.0, "c": 0.5},
)

print("A =", lin.A)  # [[0.0, 1.0], [-4.0, -0.5]]
print("B =", lin.B)  # [[0.0], [1.0]]
print("C =", lin.C)  # [[1.0, 0.0]]
print("D =", lin.D)  # [[0.0]]
```

`LinearizedSystem` stores matrices as lists of lists. NumPy can analyze them;
it is also installed by the SciPy extra used above:

```python
import numpy as np

eigenvalues = np.linalg.eigvals(np.asarray(lin.A))
print(f"Eigenvalues: {eigenvalues}")
print(f"Stable: {all(e.real < 0 for e in eigenvalues)}")  # Stable: True
```

## Nonlinear Example: Van der Pol Oscillator

This example is independent of the damped oscillator:

```python
from gds_domains.control import State
from gds_domains.symbolic import StateEquation, SymbolicControlModel

vdp = SymbolicControlModel(
    name="VanDerPol",
    states=[State(name="x1", initial=1.0), State(name="x2", initial=0.0)],
    symbolic_params=["mu"],
    state_equations=[
        StateEquation(state_name="x1", expr_str="x2"),
        StateEquation(state_name="x2", expr_str="mu*(1 - x1**2)*x2 - x1"),
    ],
)

lin_vdp = vdp.linearize(x0=[0.0, 0.0], u0=[], param_values={"mu": 1.0})
print("A =", lin_vdp.A)  # [[0.0, 1.0], [-1.0, 1.0]]
```

The origin is unstable for this positive value of `mu`. This is a local
linearization result, not a claim about the nonlinear system's entire trajectory.

## Next Steps

- [Symbolic Overview](index.md) -- architecture, types, and expression grammar
- [Continuous-Time](../continuous/index.md) -- ODE simulation engine
- [Control](../control/index.md) -- underlying structural control DSL
