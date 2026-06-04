---
layout: default
title: "08 - Post-Processing"
parent: English
nav_order: 8
---

# 08 - Post-Processing

After solving (`res = m.solve()`), you can compute bending moments, shear forces,
and displacements at any point within each element.

## Nodal results

```python
res.displacements(node)           # array [w, theta_x, theta_y]
res.displacement(node, "w")       # single DOF (float)
res.reactions(node)               # array [Fz, Mx, My]
```

## Element stresses

```python
from platefeapy import postprocess

di = postprocess.element_stresses(res, elem_id, n=5)
# Returns dict: x, y, Mx, My, Mxy, Qx, Qy
```

Components:
- `Mx`: bending moment about Y-axis (causes curvature in X-direction)
- `My`: bending moment about X-axis (causes curvature in Y-direction)
- `Mxy`: twisting moment
- `Qx`: shear force in X-direction
- `Qy`: shear force in Y-direction

The stresses are computed at `n×n` Gauss points within the element.

## Element displacements

```python
dd = postprocess.element_displacements(res, elem_id, n=11)
# Returns dict: x, y, w
```

The transverse displacement `w` is interpolated at `n×n` points using the
element shape functions.

## Global deformed shape

```python
data = postprocess.deformed_shape(res, scale=100.0, n=11)
# Returns dict: {elem_id: {x, y, w}} for all elements
```

## Principal moments

```python
M1, M2, alpha = postprocess.principal_moments(Mx, My, Mxy)
```

Returns:
- `M1`: maximum principal moment
- `M2`: minimum principal moment
- `alpha`: angle of principal direction [radians]

The principal moments are the eigenvalues of the moment tensor:

```
[Mx   Mxy]
[Mxy  My ]
```

## Complete example

```python
res = m.solve()

# Maximum deflection
w_max = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
print(f"w_max = {w_max:.4e} m")

# Moments at element center
s = postprocess.element_stresses(res, 1, n=1)
print(f"Mx = {s['Mx'][0]:.1f} Nm/m")
print(f"My = {s['My'][0]:.1f} Nm/m")
print(f"Mxy = {s['Mxy'][0]:.1f} Nm/m")

# Principal moments
M1, M2, alpha = postprocess.principal_moments(s['Mx'][0], s['My'][0], s['Mxy'][0])
print(f"M1 = {M1:.1f} Nm/m at {alpha:.2f} rad")
print(f"M2 = {M2:.1f} Nm/m")

# Shear forces
print(f"Qx = {s['Qx'][0]:.1f} N/m")
print(f"Qy = {s['Qy'][0]:.1f} N/m")
```

## Stress recovery at arbitrary points

```python
el = m.elements[eid]
ed = el.global_dofs(m.dof_map)
u_elem = res.U[ed]

# Stresses at natural coordinates (xi, eta) in [-1, 1]
s = el.stress_at(xi=0.0, eta=0.0, u_elem=u_elem)
# Returns dict: Mx, My, Mxy, Qx, Qy
```

Natural coordinates:
- `(0, 0)`: element center
- `(-1, -1)`: node 1
- `(1, -1)`: node 2
- `(1, 1)`: node 3
- `(-1, 1)`: node 4
