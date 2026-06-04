---
layout: default
title: "06 - Supports & Constraints"
parent: English
nav_order: 6
---

# 06 - Supports & Constraints

## Support types

### Fixed (clamped)

All 3 DOFs restrained: `w = 0`, `θx = 0`, `θy = 0`.

```python
m.fix(node)
```

Typical use: clamped edges, built-in supports.

### Simple support (pin)

Only transverse displacement restrained: `w = 0`, rotations free.

```python
m.pin(node)
```

Typical use: simply supported edges.

### Custom support

Selective DOF restraint:

```python
m.support(node, w=True, theta_x=True, theta_y=False)
```

## Common boundary conditions

| Condition | Code | Physical meaning |
|-----------|------|------------------|
| Clamped | `m.fix(n)` | w=0, θx=0, θy=0 |
| Simply supported | `m.pin(n)` | w=0 |
| Symmetry (x=const) | `m.support(n, theta_y=True)` | θy=0 (no rotation about Y) |
| Symmetry (y=const) | `m.support(n, theta_x=True)` | θx=0 (no rotation about X) |
| Guided | `m.support(n, theta_x=True, theta_y=True)` | θx=0, θy=0, w free |
| Free | (nothing) | No restraints |

## Symmetry conditions

For a plate with symmetry about the X-axis (at y=0):

```python
# Along the symmetry line: theta_x = 0
for nid in symmetry_nodes:
    m.support(nid, theta_x=True)
```

For symmetry about the Y-axis (at x=0):

```python
# Along the symmetry line: theta_y = 0
for nid in symmetry_nodes:
    m.support(nid, theta_y=True)
```

For double symmetry (quarter model):

```python
# Corner node: both rotations fixed
m.support(corner_node, theta_x=True, theta_y=True)
```

## Settlements

Imposed displacements (non-zero prescribed values):

```python
m.add_settlement(node, "w", -0.005)        # 5 mm downward
m.add_settlement(node, "theta_x", 0.001)   # imposed rotation
```

Settlements are applied during the solution phase and affect the load vector.

## Stability requirements

The model must have sufficient constraints to prevent rigid body motion:

- **Minimum**: at least 3 non-collinear nodes with `w` restrained
- **Recommended**: proper boundary conditions on all edges

If the stiffness matrix is singular, `solve()` raises a `ValueError`.
