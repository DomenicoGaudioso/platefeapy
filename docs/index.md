---
layout: default
title: Home
nav_order: 1
---

# platefeapy

<div align="center">
  <img src="img/Logo_PlatefeaPy.png" alt="platefeapy Logo" width="216">
</div>

A Python finite-element solver for the **static and modal analysis** of **plate structures** using Mindlin-Reissner and Kirchhoff-Love theory.

## Quick Start

```python
from platefeapy import Model, Material, ShellSection

m = Model()
m.add_node(1, 0, 0)
m.add_node(2, 1, 0)
m.add_node(3, 1, 1)
m.add_node(4, 0, 1)

mat = Material(E=210e9, nu=0.3)
sec = ShellSection(t=0.01)
m.add_plate(1, [1, 2, 3, 4], mat, sec)

for nid in range(1, 5):
    m.fix(nid, ["w"])

m.add_pressure(1, p=-1000.0)
res = m.solve()
print(res.displacements(1))
```

## Features

- **Mindlin-Reissner plate** (thick plates, shear deformable, SRI integration)
- **Kirchhoff-Love plate** (thin plates, ACM element)
- **Pressure loads** (uniform, patch)
- **Nodal loads** (forces and moments)
- **Thermal loads** (gradient through thickness)
- **Settlements** (imposed displacements/rotations)
- **Modal analysis** (natural frequencies and mode shapes)
- **Post-processing** (moments Mx, My, Mxy; shear forces Qx, Qy)
- **Plotly visualization** (mesh, deformed shape, contour plots)
