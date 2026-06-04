---
layout: default
title: "02 - Quick Start"
parent: English
nav_order: 2
---

# 02 - Quick Start

Your first model: a simply supported square plate under uniform pressure.

```python
from platefeapy import Model, Material, ShellSection

# 1. Create the model
m = Model()

# 2. Add nodes (2×2 mesh on a 1×1 m plate)
m.add_node(1, 0.0, 0.0)
m.add_node(2, 0.5, 0.0)
m.add_node(3, 1.0, 0.0)
m.add_node(4, 0.0, 0.5)
m.add_node(5, 0.5, 0.5)
m.add_node(6, 1.0, 0.5)
m.add_node(7, 0.0, 1.0)
m.add_node(8, 0.5, 1.0)
m.add_node(9, 1.0, 1.0)

# 3. Define material and section
mat = Material(E=210e9, nu=0.3)       # steel
sec = ShellSection(t=0.01)             # 10 mm thick

# 4. Add plate elements (4 quadrilaterals)
m.add_plate(1, [1, 2, 5, 4], mat, sec)
m.add_plate(2, [2, 3, 6, 5], mat, sec)
m.add_plate(3, [4, 5, 8, 7], mat, sec)
m.add_plate(4, [5, 6, 9, 8], mat, sec)

# 5. Simply supported edges (w=0 on boundary nodes)
for nid in [1, 2, 3, 4, 6, 7, 8, 9]:
    m.fix(nid, ["w"])

# 6. Apply uniform pressure
for eid in m.elements:
    m.add_pressure(eid, p=-1000.0)    # 1 kPa downward

# 7. Solve
res = m.solve()

# 8. Read results
print(res.displacements(5))   # [w, theta_x, theta_y] at center
```

## Expected result

For a simply supported square plate under uniform pressure:

```
w_max ≈ 0.00406 · p · L⁴ / D
```

where `D = E·t³ / (12·(1−ν²))` is the flexural rigidity.

```python
D = 210e9 * 0.01**3 / (12 * (1 - 0.3**2))
w_exact = 0.00406 * 1000 * 1.0**4 / D
print(f"w_max FEM   = {abs(res.displacement(5, 'w')):.6e} m")
print(f"w_max exact = {w_exact:.6e} m")
```

## Visualization

After solving, you can visualize the mesh and results:

```python
from platefeapy.plotting import plot_mesh, plot_deformed, plot_contour

plot_mesh(m).show()
plot_deformed(res, scale=100).show()
plot_contour(res, "w").show()
```

### Mesh

![Simply supported plate mesh](images/mesh_simply_supported.png)
*8×8 mesh of a simply supported square plate.*

### Deformed shape

![Simply supported plate deformed](images/deformed_simply_supported.png)
*Deformed shape (scale 100×) under uniform pressure.*

### Displacement contour

![Simply supported plate displacement](images/displacement_w_simply_supported.png)
*Transverse displacement w [m] contour plot.*

## Next steps

- [Structural Model](en-03-structural-model.md) — nodes, materials, sections, elements
- [Element Types](en-04-element-types.md) — Mindlin vs Kirchhoff
- [Loads](en-05-loads.md) — pressure, nodal, thermal, settlements
- [Post-Processing](en-08-post-processing.md) — moments, shear, displacements
