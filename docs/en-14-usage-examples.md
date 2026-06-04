---
layout: default
title: "14 - Usage Examples"
parent: English
nav_order: 14
---

# 14 - Usage Examples

The `usage_examples/` directory contains self-contained scripts covering every feature.

## Available examples

| # | File | Description |
|---|------|-------------|
| 01 | `01_convergence_ss_plate.py` | Convergence study: simply supported plate vs Navier solution |
| 02 | `02_clamped_plate.py` | Clamped plate under uniform pressure |
| 03 | `03_modal_analysis.py` | Modal analysis of a simply supported plate |

## Running examples

```bash
cd platefeapy
python usage_examples/01_convergence_ss_plate.py
```

## Example 01: Convergence study

Simply supported square plate (L=1m, t=10mm, p=1kPa) with progressive mesh
refinement:

```python
from platefeapy import Model, Material, ShellSection

L = 1.0
p = -1000.0
E = 210e9
nu = 0.3
t = 0.01

for n_el in [2, 4, 8, 12, 16]:
    m = Model()
    # ... create mesh with n_el × n_el elements ...
    # ... apply simply supported BCs ...
    # ... apply uniform pressure ...
    res = m.solve()
    w_max = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    # ... compare with analytical solution ...
```

Expected output:

```
Mesh  2x 2  |  w_max = 3.85e-05  |  esatto = 4.06e-05  |  err = 5.17%
Mesh  4x 4  |  w_max = 4.00e-05  |  esatto = 4.06e-05  |  err = 1.48%
Mesh  8x 8  |  w_max = 4.04e-05  |  esatto = 4.06e-05  |  err = 0.49%
Mesh 12x12  |  w_max = 4.05e-05  |  esatto = 4.06e-05  |  err = 0.22%
Mesh 16x16  |  w_max = 4.06e-05  |  esatto = 4.06e-05  |  err = 0.12%
```

## Example 02: Clamped plate

All edges clamped (w=0, θx=0, θy=0):

```python
for nid in boundary_nodes:
    m.fix(nid)    # all 3 DOFs
```

Analytical solution: `w_max = 0.00126 · p · L⁴ / D`

## Example 03: Modal analysis

Natural frequencies of a simply supported plate compared with the Navier
analytical solution:

```python
mr = m.modal(n_modes=6)

# Analytical frequencies
f_mn = (π / (2·L²)) · √(D / (ρ·t)) · (m² + n²)
```

## Basic examples

The `examples/` directory contains simpler scripts:

| File | Description |
|------|-------------|
| `ex01_simply_supported.py` | SS plate with uniform pressure |
| `ex02_clamped.py` | Clamped plate with uniform pressure |
| `ex03_point_load.py` | Plate with concentrated load |

```bash
python examples/ex01_simply_supported.py
```
