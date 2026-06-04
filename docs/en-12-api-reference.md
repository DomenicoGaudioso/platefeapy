---
layout: default
title: "12 - API Reference"
parent: English
nav_order: 12
---

# 12 - API Reference

Complete reference of all public functions in **platefeapy**.

Typical import:

```python
from platefeapy import Model, Material, ShellSection
from platefeapy import postprocess
from platefeapy.plotting import (plot_mesh, plot_deformed, plot_contour,
                                  plot_reactions, plot_mode)
```

---

## Materials and Sections

### `Material(E, nu=0.3, alpha=0.0, G=None, rho=0.0, name="")`
Isotropic elastic material. `G` (shear modulus) is derived as
`E/(2(1+nu))` if not provided. `alpha` = thermal expansion; `rho` = density.

### `ShellSection(t, kappa=5/6, name="")`
Plate section properties.
- `t`: thickness [m]
- `kappa`: shear correction factor (default 5/6 for Mindlin plates)

Methods:
- `D_bending(E, nu)` → `E·t³/(12·(1−ν²))`
- `D_shear(G)` → `κ·G·t`
- `D_membrane(E, nu)` → `E·t/(1−ν²)`

---

## Model

### `Model()`
FEM model container. Attributes: `nodes`, `elements`, `nodal_loads`,
`pressure_loads`, `thermal_loads`, `settlements`.

### `add_node(id, x, y) -> Node`
Add a node (3 DOFs: `w, theta_x, theta_y`).

### `add_plate(id, node_ids, material, section, theory="mindlin") -> MindlinPlateQ4 | KirchhoffPlateQ4`
Quadrilateral plate element (4 nodes).
- `node_ids`: list of 4 node IDs (counter-clockwise order)
- `theory`: `"mindlin"` (default, SRI) or `"kirchhoff"` (ACM)

### Constraints
- **`fix(node, dofs=None)`** — restrain listed DOFs (`["w","theta_x","theta_y"]`); `None` = all 3 (clamped).
- **`pin(node)`** — simple support: restrains `w` only.
- **`support(node, w=False, theta_x=False, theta_y=False)`** — selective constraint.

### `add_settlement(node, dof, value) -> Settlement`
Settlement (imposed displacement/rotation): `dof` ∈ `{w, theta_x, theta_y}`.

---

## Loads

All `add_*` methods accept `case="..."` (load case, default `"default"`).

### `add_nodal_load(node, case="default", Fz=0, Mx=0, My=0) -> NodalLoad`
Concentrated force/moment at a node (global system).

### `add_pressure(elem, p, case="default") -> PressureLoad`
Uniform pressure on element surface [Pa]. Positive = +Z direction.

### `add_patch_load(elem, p, xi_range=(-1,1), eta_range=(-1,1), case="default") -> PatchLoad`
Pressure on a portion of the element (natural coordinates).

### `add_thermal_load(elem, dT, case="default") -> ThermalLoad`
Temperature gradient through thickness [°C]. Produces curvature `κ = α·ΔT/t`.

---

## Solution

### `load_cases() -> list[str]`
Sorted list of load cases present in the loads.

### `solve(sparse=False, cases=None) -> Result`
Solve the system.
- `sparse`: `True` uses scipy sparse solver (large models).
- `cases`: load combination —
  - `None` = all loads (coeff 1);
  - string = a single load case;
  - list/set = combination (coeff 1 each);
  - **dict `{case: coefficient}`** = combination with multiplicative coefficients.

### `modal(n_modes=10) -> ModalResult`
Modal analysis: solves `K φ = ω² M φ`. Requires `rho > 0` in materials.

---

## Results

### `Result`
Attributes: `U` (global displacements), `R` (global reactions),
`element_forces` (local end forces per element, 12).

- **`displacements(node) -> ndarray(3)`** — `[w, theta_x, theta_y]` of the node.
- **`displacement(node, dof) -> float`** — single component.
- **`reactions(node) -> ndarray(3)`** — `[Fz, Mx, My]` of the node.

### `ModalResult`
Attributes: `omega` [rad/s], `freq` [Hz], `period` [s], `phi` (ndof × n_modes).

- **`mode(i) -> ndarray(ndof)`** — i-th mode shape vector.
- **`mode_shape(i, node) -> ndarray(3)`** — `[w, theta_x, theta_y]` at node.

---

## Post-processing (`platefeapy.postprocess`)

### `element_stresses(result, elem_id, n=5) -> dict`
Stresses at `n×n` Gauss points. Returns `{x, y, Mx, My, Mxy, Qx, Qy}`.

### `element_displacements(result, elem_id, n=11) -> dict`
Displacements at `n×n` points. Returns `{x, y, w}`.

### `deformed_shape(result, scale=1.0, n=11) -> dict`
Deformed coordinates for all elements. Returns `{elem_id: {x, y, w}}`.

### `principal_moments(Mx, My, Mxy) -> tuple[float, float, float]`
Principal moments and angle: `(M1, M2, alpha)`.

---

## Visualization (`platefeapy.plotting`)

Requires the `plot` extra (`plotly`, `kaleido`). Each function returns a
`plotly.graph_objects.Figure`.

- **`plot_mesh(model, show_node_ids=True)`** — 2D mesh with node IDs.
- **`plot_deformed(result, scale=1.0, n=21)`** — 3D deformed shape.
- **`plot_contour(result, component="Mx", n=11)`** — 2D contour map.
- **`plot_reactions(result, scale=1.0)`** — support reactions.
- **`plot_mode(modal_result, i=0, scale=1.0, n=21)`** — i-th mode shape.
